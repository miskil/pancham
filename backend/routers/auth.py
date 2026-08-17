import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.village_user import VillageUser
from ..models.admin_user import AdminUser
from ..models.password_reset_token import PasswordResetToken
from ..auth import verify_password, create_token, hash_password, require_role
from ..config import settings
from ..utils.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

GENERIC_FORGOT_PASSWORD_MESSAGE = "If an account with that email is on file, a reset link has been sent."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    village_id: str | None = None
    village_user_type: str | None = None
    must_change_password: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    username_or_email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    # --- Donor ---
    if settings.donor_token and body.username == "donor" and body.password == settings.donor_token:
        token = create_token(subject="donor", role="DONOR")
        return TokenResponse(access_token=token, role="DONOR")

    # --- Admin ---
    admin_result = await db.execute(
        select(AdminUser).where(AdminUser.login_username == body.username, AdminUser.is_active == True)  # noqa: E712
    )
    admin = admin_result.scalar_one_or_none()
    if admin and verify_password(body.password, admin.login_password_hash):
        token = create_token(subject=admin.login_username, role="ADMIN", admin_id=admin.id)
        return TokenResponse(access_token=token, role="ADMIN", must_change_password=admin.must_change_password)

    # Fallback admin login from environment to avoid lockout on fresh/reset DB.
    if body.username == settings.admin_username and body.password == settings.admin_password:
        token = create_token(subject=settings.admin_username, role="ADMIN")
        return TokenResponse(access_token=token, role="ADMIN", must_change_password=False)

    # --- Village ---
    vu_result = await db.execute(
        select(VillageUser).where(VillageUser.login_username == body.username, VillageUser.is_active == True)  # noqa: E712
    )
    vu = vu_result.scalar_one_or_none()
    if not vu or not verify_password(body.password, vu.login_password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(
        subject=vu.login_username,
        role="VILLAGE",
        village_id=vu.village_id,
        village_user_type=vu.user_type,
    )
    return TokenResponse(
        access_token=token,
        role="VILLAGE",
        village_id=vu.village_id,
        village_user_type=vu.user_type,
        must_change_password=vu.must_change_password,
    )


@router.post("/village/change-password")
async def village_change_password(body: ChangePasswordRequest, db: AsyncSession = Depends(get_db), user=Depends(require_role("VILLAGE"))):
    result = await db.execute(
        select(VillageUser).where(VillageUser.village_id == user["village_id"], VillageUser.login_username == user["sub"])
    )
    vu = result.scalar_one_or_none()
    if not vu or not verify_password(body.current_password, vu.login_password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    vu.login_password_hash = hash_password(body.new_password)
    vu.must_change_password = False
    await db.commit()
    return {"ok": True}


@router.post("/admin/change-password")
async def admin_change_password(body: ChangePasswordRequest, db: AsyncSession = Depends(get_db), user=Depends(require_role("ADMIN"))):
    result = await db.execute(
        select(AdminUser).where(AdminUser.login_username == user["sub"])
    )
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(body.current_password, admin.login_password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    admin.login_password_hash = hash_password(body.new_password)
    admin.must_change_password = False
    await db.commit()
    return {"ok": True}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    identifier = body.username_or_email.strip()

    user_type: str | None = None
    user_id: str | None = None
    email: str | None = None

    admin_result = await db.execute(
        select(AdminUser).where(
            (AdminUser.login_username == identifier) | (AdminUser.email == identifier),
            AdminUser.is_active == True,  # noqa: E712
        )
    )
    admin = admin_result.scalar_one_or_none()
    if admin and admin.email:
        user_type, user_id, email = "ADMIN", admin.id, admin.email

    if not user_type:
        vu_result = await db.execute(
            select(VillageUser).where(
                (VillageUser.login_username == identifier) | (VillageUser.email == identifier),
                VillageUser.is_active == True,  # noqa: E712
            )
        )
        vu = vu_result.scalar_one_or_none()
        if vu and vu.email:
            user_type, user_id, email = "VILLAGE", vu.id, vu.email

    if user_type:
        raw_token = secrets.token_urlsafe(32)
        db.add(
            PasswordResetToken(
                user_type=user_type,
                user_id=user_id,
                token_hash=_hash_token(raw_token),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_expire_minutes),
            )
        )
        await db.commit()
        reset_link = f"{settings.frontend_url}/?reset_token={raw_token}"
        await send_email(
            email,
            "Reset your Pancham password",
            "You requested a password reset for your Pancham account.\n\n"
            f"Reset your password here: {reset_link}\n\n"
            f"This link expires in {settings.password_reset_token_expire_minutes} minutes. "
            "If you did not request this, you can ignore this email.",
        )

    # Same response whether or not a match was found, so usernames/emails can't be enumerated.
    return {"ok": True, "message": GENERIC_FORGOT_PASSWORD_MESSAGE}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")

    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == _hash_token(body.token))
    )
    reset_token = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not reset_token or reset_token.used_at is not None or reset_token.expires_at < now:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    if reset_token.user_type == "ADMIN":
        user_result = await db.execute(select(AdminUser).where(AdminUser.id == reset_token.user_id))
    else:
        user_result = await db.execute(select(VillageUser).where(VillageUser.id == reset_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="This reset link is invalid or has expired")

    user.login_password_hash = hash_password(body.new_password)
    user.must_change_password = False
    reset_token.used_at = now
    await db.commit()
    return {"ok": True}

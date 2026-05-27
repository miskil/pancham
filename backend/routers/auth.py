from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.village import Village
from ..auth import verify_password, create_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = None  # set via env or seed script


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    village_id: str | None = None


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    if body.username == settings.admin_username and body.password == settings.admin_password:
        token = create_token(subject=settings.admin_username, role="ADMIN")
        return TokenResponse(access_token=token, role="ADMIN")

    if settings.donor_token and body.username == "donor" and body.password == settings.donor_token:
        token = create_token(subject="donor", role="DONOR")
        return TokenResponse(access_token=token, role="DONOR")

    result = await db.execute(select(Village).where(Village.login_username == body.username, Village.is_active == True))  # noqa: E712
    village = result.scalar_one_or_none()
    if not village or not verify_password(body.password, village.login_password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(subject=village.login_username, role="VILLAGE", village_id=village.id)
    return TokenResponse(access_token=token, role="VILLAGE", village_id=village.id)

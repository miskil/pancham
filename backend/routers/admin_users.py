import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.admin_user import AdminUser
from ..auth import hash_password, require_role

router = APIRouter(prefix="/admin/users", tags=["admin-users"])
admin_only = require_role("ADMIN")


class AdminUserOut(BaseModel):
    id: str
    display_name: str | None
    login_username: str
    is_active: bool
    must_change_password: bool
    temp_password: str | None = None

    class Config:
        from_attributes = True


class CreateAdminUserRequest(BaseModel):
    login_username: str
    display_name: str | None = None


@router.get("", response_model=list[AdminUserOut])
async def list_admin_users(db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(AdminUser).order_by(AdminUser.created_at))
    return result.scalars().all()


@router.post("", response_model=AdminUserOut)
async def create_admin_user(body: CreateAdminUserRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    existing = await db.execute(select(AdminUser).where(AdminUser.login_username == body.login_username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")

    temp_password = secrets.token_urlsafe(10)
    admin = AdminUser(
        login_username=body.login_username,
        display_name=body.display_name,
        login_password_hash=hash_password(temp_password),
        must_change_password=True,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return AdminUserOut(
        id=admin.id,
        display_name=admin.display_name,
        login_username=admin.login_username,
        is_active=admin.is_active,
        must_change_password=admin.must_change_password,
        temp_password=temp_password,
    )


@router.patch("/{user_id}/deactivate")
async def deactivate_admin_user(user_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(admin_only)):
    result = await db.execute(select(AdminUser).where(AdminUser.id == user_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    if admin.login_username == current_user["sub"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    admin.is_active = False
    await db.commit()
    return {"ok": True}


@router.patch("/{user_id}/reset-password")
async def reset_admin_password(user_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(AdminUser).where(AdminUser.id == user_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    temp_password = secrets.token_urlsafe(10)
    admin.login_password_hash = hash_password(temp_password)
    admin.must_change_password = True
    admin.is_active = True
    await db.commit()
    return {"ok": True, "temp_password": temp_password, "login_username": admin.login_username}

from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import require_role
from ..utils.storage import save_upload
from ..db import get_db
from ..models.admin_user import AdminUser
from ..models.anubhav import AnubhavMediaFile, AnubhavPost
from ..models.village import Village

router = APIRouter(prefix="/anubhav", tags=["anubhav"])
any_user = require_role("ADMIN", "VILLAGE")


class AnubhavPostIn(BaseModel):
    title: str
    body: str


class AnubhavPostOut(BaseModel):
    class MediaOut(BaseModel):
        id: str
        media_type: str
        file_url: str
        uploaded_at: str

        class Config:
            from_attributes = True

    id: str
    title: str
    body: str
    author_role: str
    author_village_id: str | None = None
    author_admin_id: str | None = None
    author_display_name: str
    can_edit: bool
    media_files: list[MediaOut]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def _serialize(post: AnubhavPost, user: dict) -> AnubhavPostOut:
    role = user.get("role")
    if role == "ADMIN":
        can_edit = post.author_role == "ADMIN" and post.author_admin_id == user.get("admin_id")
    else:
        can_edit = post.author_role == "VILLAGE" and post.author_village_id == user.get("village_id")
    return AnubhavPostOut(
        id=post.id,
        title=post.title,
        body=post.body,
        author_role=post.author_role,
        author_village_id=post.author_village_id,
        author_admin_id=post.author_admin_id,
        author_display_name=post.author_display_name,
        can_edit=can_edit,
        media_files=[
            AnubhavPostOut.MediaOut(
                id=m.id,
                media_type=m.media_type,
                file_url=m.file_url,
                uploaded_at=m.uploaded_at.isoformat(),
            )
            for m in post.media_files
        ],
        created_at=post.created_at.isoformat(),
        updated_at=post.updated_at.isoformat(),
    )


@router.get("/posts", response_model=list[AnubhavPostOut])
async def list_posts(db: AsyncSession = Depends(get_db), user=Depends(any_user)):
    result = await db.execute(
        select(AnubhavPost)
        .options(selectinload(AnubhavPost.media_files))
        .order_by(AnubhavPost.created_at.desc())
    )
    posts = result.scalars().all()
    return [_serialize(p, user) for p in posts]


@router.post("/posts", response_model=AnubhavPostOut, status_code=201)
async def create_post(body: AnubhavPostIn, db: AsyncSession = Depends(get_db), user=Depends(any_user)):
    role = user.get("role")
    if role == "ADMIN":
        admin_id = user.get("admin_id")
        if not admin_id:
            raise HTTPException(status_code=400, detail="Admin ID not found in token")
        result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
        admin = result.scalar_one_or_none()
        display_name = (admin.display_name or admin.login_username) if admin else "Admin"
        post = AnubhavPost(
            title=body.title,
            body=body.body,
            author_role="ADMIN",
            author_admin_id=admin_id,
            author_display_name=display_name,
        )
    else:
        village_id = user.get("village_id")
        result = await db.execute(select(Village).where(Village.id == village_id))
        village = result.scalar_one_or_none()
        display_name = village.name if village else "Village"
        post = AnubhavPost(
            title=body.title,
            body=body.body,
            author_role="VILLAGE",
            author_village_id=village_id,
            author_display_name=display_name,
        )
    db.add(post)
    await db.commit()
    result = await db.execute(
        select(AnubhavPost)
        .options(selectinload(AnubhavPost.media_files))
        .where(AnubhavPost.id == post.id)
    )
    created = result.scalar_one()
    return _serialize(created, user)


@router.patch("/posts/{post_id}", response_model=AnubhavPostOut)
async def update_post(post_id: str, body: AnubhavPostIn, db: AsyncSession = Depends(get_db), user=Depends(any_user)):
    result = await db.execute(
        select(AnubhavPost)
        .options(selectinload(AnubhavPost.media_files))
        .where(AnubhavPost.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    _assert_can_edit(post, user)
    post.title = body.title
    post.body = body.body
    post.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(post)
    return _serialize(post, user)


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: str, db: AsyncSession = Depends(get_db), user=Depends(any_user)):
    result = await db.execute(select(AnubhavPost).where(AnubhavPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    _assert_can_edit(post, user)
    await db.delete(post)
    await db.commit()


@router.post("/posts/{post_id}/media", response_model=AnubhavPostOut.MediaOut)
async def upload_post_media(
    post_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(any_user),
):
    result = await db.execute(select(AnubhavPost).where(AnubhavPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    _assert_can_edit(post, user)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    file_url = await save_upload(file.file, file.filename, "anubhav")

    media = AnubhavMediaFile(
        anubhav_post_id=post_id,
        media_type="PHOTO",
        file_url=file_url,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return AnubhavPostOut.MediaOut(
        id=media.id,
        media_type=media.media_type,
        file_url=media.file_url,
        uploaded_at=media.uploaded_at.isoformat(),
    )


def _assert_can_edit(post: AnubhavPost, user: dict):
    role = user.get("role")
    if role == "ADMIN":
        if post.author_role != "ADMIN" or post.author_admin_id != user.get("admin_id"):
            raise HTTPException(status_code=403, detail="You can only edit your own posts")
    else:
        if post.author_role != "VILLAGE" or post.author_village_id != user.get("village_id"):
            raise HTTPException(status_code=403, detail="You can only edit your own posts")

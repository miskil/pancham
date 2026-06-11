import io
import os
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..auth import require_role
from ..db import get_db
from ..models.anubhav import AnubhavMediaFile, AnubhavPost
from ..models.evidence import SupportEvidence
from ..models.status_update import MediaFile, StatusUpdate
from ..models.village import Village
from ..utils.storage import UPLOAD_ROOT

router = APIRouter(prefix="/admin/storage", tags=["admin-storage"])
admin_only = require_role("ADMIN")


class FolderStats(BaseModel):
    name: str
    file_count: int
    size_bytes: int


class StorageStats(BaseModel):
    total_bytes: int
    used_bytes: int
    free_bytes: int
    folders: list[FolderStats]


def _folder_stats(path: str) -> FolderStats:
    p = Path(path)
    if not p.exists():
        return FolderStats(name=p.name, file_count=0, size_bytes=0)
    files = list(p.rglob("*"))
    total = sum(f.stat().st_size for f in files if f.is_file())
    count = sum(1 for f in files if f.is_file())
    return FolderStats(name=p.name, file_count=count, size_bytes=total)


@router.get("/stats", response_model=StorageStats)
async def get_storage_stats(_=Depends(admin_only)):
    root = Path(UPLOAD_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    usage = os.statvfs(root)
    total = usage.f_frsize * usage.f_blocks
    free = usage.f_frsize * usage.f_bavail
    used = total - free

    folders = [
        _folder_stats(str(root / "media")),
        _folder_stats(str(root / "evidence")),
        _folder_stats(str(root / "anubhav")),
    ]
    return StorageStats(total_bytes=total, used_bytes=used, free_bytes=free, folders=folders)


@router.get("/archive")
async def download_archive(
    village_id: str | None = Query(None),
    types: str = Query("media,evidence,anubhav"),
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    """Stream a ZIP of uploaded assets, optionally filtered by village and asset type."""
    want = {t.strip() for t in types.split(",")}
    root = Path(UPLOAD_ROOT)

    # Collect (disk_path, archive_path) pairs
    entries: list[tuple[Path, str]] = []

    if "media" in want:
        q = select(MediaFile).options(selectinload(MediaFile.status_update))
        if village_id:
            q = q.join(StatusUpdate).where(StatusUpdate.village_id == village_id)
        result = await db.execute(q)
        for mf in result.scalars().all():
            disk = _url_to_path(mf.file_url, root)
            if disk and disk.exists():
                label = _village_label(mf.status_update.village_id if mf.status_update else "unknown")
                entries.append((disk, f"{label}/media/{disk.name}"))

    if "evidence" in want:
        q = select(SupportEvidence)
        if village_id:
            q = q.where(SupportEvidence.village_id == village_id)
        result = await db.execute(q)
        for ev in result.scalars().all():
            disk = _url_to_path(ev.file_url, root)
            if disk and disk.exists():
                label = _village_label(ev.village_id)
                entries.append((disk, f"{label}/evidence/{disk.name}"))

    if "anubhav" in want:
        q = select(AnubhavMediaFile).options(selectinload(AnubhavMediaFile.post))
        if village_id:
            q = q.join(AnubhavPost).where(AnubhavPost.author_village_id == village_id)
        result = await db.execute(q)
        for am in result.scalars().all():
            disk = _url_to_path(am.file_url, root)
            if disk and disk.exists():
                vid = (am.post.author_village_id if am.post else None) or "admin"
                label = _village_label(vid)
                entries.append((disk, f"{label}/anubhav/{disk.name}"))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for disk_path, arc_name in entries:
            zf.write(disk_path, arc_name)
    buf.seek(0)

    tag = village_id or "all"
    filename = f"pancham-assets-{tag}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _url_to_path(file_url: str, root: Path) -> Path | None:
    """Convert a stored /uploads/... URL to an absolute disk path."""
    if not file_url or not file_url.startswith("/uploads/"):
        return None
    relative = file_url[len("/uploads/"):]
    return root / relative


def _village_label(village_id: str) -> str:
    return village_id[:8] if village_id else "unknown"

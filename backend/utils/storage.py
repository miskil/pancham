import asyncio
import os
import shutil
import uuid

UPLOAD_ROOT = os.getenv("UPLOAD_DIR", "uploads")


async def save_upload(file_obj, original_filename: str, subfolder: str) -> str:
    """Save an uploaded file to the persistent volume and return its URL path."""
    ext = os.path.splitext(original_filename or "")[1].lower()
    safe_name = f"{uuid.uuid4()}{ext}"
    dest_dir = os.path.join(UPLOAD_ROOT, subfolder)
    dest = os.path.join(dest_dir, safe_name)
    await asyncio.to_thread(_write_file, file_obj, dest_dir, dest)
    return f"/uploads/{subfolder}/{safe_name}"


def _write_file(file_obj, dest_dir: str, dest: str) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file_obj, f)

import os
import shutil
import uuid

UPLOAD_ROOT = os.getenv("UPLOAD_DIR", "uploads")


def save_upload(file_obj, original_filename: str, subfolder: str) -> str:
    """Save an uploaded file to the persistent volume and return its URL path."""
    dest_dir = os.path.join(UPLOAD_ROOT, subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{original_filename}"
    dest = os.path.join(dest_dir, safe_name)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file_obj, f)
    return f"/uploads/{subfolder}/{safe_name}"

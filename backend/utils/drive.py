import io
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_service():
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set")
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def upload_docx(filename: str, content: bytes, folder_id: str) -> dict:
    """Upload a .docx bytes buffer to Drive. Returns {file_id, web_view_link}."""
    service = _get_service()
    metadata = {
        "name": filename,
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "parents": [folder_id],
    }
    media = MediaIoBaseUpload(
        io.BytesIO(content),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=False,
    )
    file = service.files().create(body=metadata, media_body=media, fields="id,webViewLink").execute()
    # Make it readable by anyone with the link
    service.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return {"file_id": file["id"], "web_view_link": file["webViewLink"]}

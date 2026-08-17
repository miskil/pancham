import asyncio
import smtplib
from email.message import EmailMessage
from ..config import settings


def _send_sync(to_email: str, subject: str, body: str) -> None:
    if not settings.smtp_host:
        print(f"[email:not-configured] To={to_email} Subject={subject}\n{body}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)


async def send_email(to_email: str, subject: str, body: str) -> None:
    await asyncio.to_thread(_send_sync, to_email, subject, body)

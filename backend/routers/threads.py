from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.thread import UpdateThread
from ..auth import get_current_user

router = APIRouter(prefix="/threads", tags=["threads"])


class MessageBody(BaseModel):
    message: str


class MessageOut(BaseModel):
    id: str
    author_role: str
    message: str
    sent_at: str

    class Config:
        from_attributes = True


@router.post("/{update_id}/messages", response_model=MessageOut)
async def post_message(update_id: str, body: MessageBody, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    msg = UpdateThread(status_update_id=update_id, author_role=user["role"], message=body.message)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return MessageOut(id=msg.id, author_role=msg.author_role, message=msg.message, sent_at=msg.sent_at.isoformat())


@router.get("/{update_id}/messages", response_model=list[MessageOut])
async def get_messages(update_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(UpdateThread).where(UpdateThread.status_update_id == update_id).order_by(UpdateThread.sent_at)
    )
    msgs = result.scalars().all()
    return [MessageOut(id=m.id, author_role=m.author_role, message=m.message, sent_at=m.sent_at.isoformat()) for m in msgs]

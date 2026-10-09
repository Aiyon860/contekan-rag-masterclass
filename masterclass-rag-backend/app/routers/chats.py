from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from sqlmodel import delete as sql_delete

from ..db import get_session
from ..models import Chat, Document, Message
from ..schemas import ChatPatch, SendMessage
from ..services import rag

router = APIRouter(prefix="/chats", tags=["chats"])
SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"}


@router.get("")
def list_chats(session: Session = Depends(get_session)):
    return session.exec(select(Chat).order_by(Chat.updated_at.desc())).all()


@router.patch("/{chat_id}")
def rename(chat_id: str, body: ChatPatch, session: Session = Depends(get_session)):
    chat = session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat tidak ditemukan.")
    chat.title = body.title
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


@router.delete("/{chat_id}", status_code=204)
def delete(chat_id: str, session: Session = Depends(get_session)):
    chat = session.get(Chat, chat_id)
    if chat:
        session.exec(sql_delete(Message).where(Message.chat_id == chat_id))
        session.delete(chat)
        session.commit()


@router.get("/{chat_id}/messages")
def messages(chat_id: str, session: Session = Depends(get_session)):
    rows = session.exec(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)).all()
    alive = {d.id for d in session.exec(select(Document)).all()}
    out = []
    for m in rows:
        d = m.model_dump()
        d["sources"] = [{**s, "deleted": s["document_id"] not in alive} for s in (m.sources or [])]
        d["attachments"] = [{**a, "deleted": a["document_id"] not in alive} for a in (m.attachments or [])]
        out.append(d)
    return out


@router.post("/{chat_id}/messages")
async def send(chat_id: str, body: SendMessage):
    gen = rag.stream_answer(chat_id, body.content.strip(), body.user_message_id, body.assistant_message_id, attachment_ids=body.attachment_ids)
    return StreamingResponse(gen, media_type="text/event-stream", headers=SSE_HEADERS)


@router.post("/{chat_id}/regenerate")
async def regenerate(chat_id: str, session: Session = Depends(get_session)):
    last_user = session.exec(
        select(Message).where(Message.chat_id == chat_id, Message.role == "user").order_by(Message.created_at.desc())
    ).first()
    if not last_user:
        raise HTTPException(404, "Belum ada pertanyaan untuk diulang.")
    gen = rag.stream_answer(chat_id, last_user.content, None, None, regenerate=True)
    return StreamingResponse(gen, media_type="text/event-stream", headers=SSE_HEADERS)

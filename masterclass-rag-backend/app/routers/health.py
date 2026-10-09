from fastapi import APIRouter

from ..config import config
from ..services import llm

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    try:
        names = [m.model for m in llm.client.list().models]
    except Exception as e:
        return {"ollama": False, "error": str(e), "missing_models": []}
    from ..models import AppSettings
    from sqlmodel import Session
    from ..db import engine

    with Session(engine) as s:
        chat_model = s.get(AppSettings, 1).chat_model
    missing = [m for m in (config.embed_model, chat_model) if m not in names]
    return {"ollama": True, "missing_models": missing}

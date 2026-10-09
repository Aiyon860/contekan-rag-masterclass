from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..db import get_session
from ..models import DEFAULT_SYSTEM_PROMPT, AppSettings
from ..schemas import SettingsUpdate
from ..services import llm

router = APIRouter(prefix="/settings", tags=["settings"])


def _out(s: AppSettings) -> dict:
    return {**s.model_dump(exclude={"id"}), "default_system_prompt": DEFAULT_SYSTEM_PROMPT}


@router.get("")
def get_settings(session: Session = Depends(get_session)):
    return _out(session.get(AppSettings, 1))


@router.put("")
def update_settings(body: SettingsUpdate, session: Session = Depends(get_session)):
    s = session.get(AppSettings, 1)
    for k, v in body.model_dump().items():
        setattr(s, k, v)
    session.add(s)
    session.commit()
    session.refresh(s)  # setelah commit atribut expired; tanpa refresh model_dump() kosong
    return _out(s)


@router.get("/models")
def models():
    try:
        return {"models": llm.list_chat_models()}
    except Exception:
        return {"models": []}

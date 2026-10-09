from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import Session, SQLModel, select

from .db import engine
from .models import DEFAULT_SYSTEM_PROMPT, LEGACY_PROMPTS, AppSettings, Document
from .routers import chats, documents, health, settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    SQLModel.metadata.create_all(engine)
    with engine.begin() as conn:  # migrasi ringan: create_all tidak meng-alter tabel yang sudah ada
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(message)"))}
        if "attachments" not in cols:
            conn.execute(text("ALTER TABLE message ADD COLUMN attachments JSON NOT NULL DEFAULT '[]'"))
        if "grounded" not in cols:
            conn.execute(text("ALTER TABLE message ADD COLUMN grounded BOOLEAN NOT NULL DEFAULT 1"))
    with Session(engine) as s:
        cfg = s.get(AppSettings, 1)
        if not cfg:
            s.add(AppSettings())
        elif cfg.system_prompt in LEGACY_PROMPTS:  # prompt strict lama yang belum pernah diedit user
            cfg.system_prompt = DEFAULT_SYSTEM_PROMPT
            s.add(cfg)
        # dokumen yang masih 'processing' saat server mati tidak akan selesai sendiri
        for d in s.exec(select(Document).where(Document.status == "processing")).all():
            d.status, d.error = "failed", "Proses terhenti karena server dimatikan. Upload ulang ya."
            s.add(d)
        s.commit()
    yield


app = FastAPI(title="Masterclass RAG", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
for r in (health.router, settings.router, documents.router, chats.router):
    app.include_router(r, prefix="/api")

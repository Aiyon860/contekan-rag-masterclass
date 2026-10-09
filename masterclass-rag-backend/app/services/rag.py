import asyncio
import re
import json
import threading
from collections.abc import AsyncIterator

from sqlmodel import Session, select

from ..config import config
from ..db import engine
from ..models import AppSettings, Chat, Document, Message, now
from . import llm, vectorstore

GENERAL_PROMPT = (
    "Kamu asisten yang ramah. Jawab dengan bahasa yang sama dengan pertanyaan user. "
    "Kamu HANYA boleh menjawab pengetahuan umum yang terkenal dan pasti benar (geografi, sains, sejarah, "
    "matematika, tokoh dunia yang sangat terkenal). "
    "Untuk pertanyaan tentang orang, nama, perusahaan, atau data tertentu yang tidak terkenal, JANGAN menebak "
    "atau mengarang. Jawab persis: \"Aku nggak nemu info itu di dokumen, dan aku juga nggak punya pengetahuan tentangnya.\""
)


FOLLOWUP_MAX_WORDS = 12
# Kata penanda pertanyaan lanjutan yang merujuk jawaban sebelumnya
FOLLOWUP_CUES = re.compile(
    r"\b(lagi|tadi|itu|ini|kok|kenapa|mengapa|salah|benar|bener|yakin|telaah|periksa|cek|ulang|ulangi|"
    r"jelaskan|jelasin|detail|rinci|maksud|darimana|dari mana|masa|serius|lanjut|terus|bagaimana bisa|"
    r"why|again|really|wrong|explain|sure|check)\b", re.I)
# Hanya pertanyaan yang benar-benar menghitung. "berapa jumlah upah" itu pencarian/perbandingan nilai; petunjuk
# hitung justru membingungkan model (uji: qwen2.5:3b turun dari 5/5 ke 2/5).
COUNT_CUES = re.compile(r"\b(ada berapa|berapa banyak|berapa kali|hitung|banyaknya|how many|count)\b", re.I)
COUNT_HINT = (
    "Petunjuk: ini pertanyaan menghitung. Telusuri baris demi baris di konteks, sebutkan baris yang cocok "
    "(nomor atau namanya), lalu tulis totalnya."
)


def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def build_prompt(question: str, sources: list[dict]) -> str:
    ctx = "\n\n".join(f"[{i + 1}] ({s['document_name']}) {s['text']}" for i, s in enumerate(sources))
    note = "\n(Konteks ini dipakai ulang dari jawaban sebelumnya karena pertanyaan terbaru berupa pertanyaan lanjutan.)" if any(s.get("reused") for s in sources) else ""
    hint = f"\n{COUNT_HINT}" if COUNT_CUES.search(question) else ""
    return f"Konteks:\n{ctx}{note}\n\nPertanyaan: {question}{hint}"


async def stream_answer(
    chat_id: str,
    question: str,
    user_msg_id: str | None,
    asst_msg_id: str | None,
    regenerate: bool = False,
    attachment_ids: list[str] | None = None,
) -> AsyncIterator[str]:
    attachment_ids = attachment_ids or []
    with Session(engine) as s:
        settings = s.get(AppSettings, 1)
        chat = s.get(Chat, chat_id)
        if chat is None:
            chat = Chat(id=chat_id, title=question[:50].strip() or "Chat baru")
            s.add(chat)
        history_rows = s.exec(
            select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
        ).all()
        history = [
            {"role": m.role, "content": m.content}
            for m in history_rows
            if m.status != "error" and m.content
        ][-config.history_messages :]

        prior_rows = [m for m in history_rows if m.role == "assistant" and m.sources]
        if regenerate and history_rows and history_rows[-1].role == "assistant":
            prior_rows = [m for m in prior_rows if m.id != history_rows[-1].id]
        prev_sources = list(prior_rows[-1].sources) if prior_rows else []

        if regenerate:
            last = history_rows[-1] if history_rows else None
            if last and last.role == "assistant":
                s.delete(last)
                if history and history[-1]["role"] == "assistant":
                    history.pop()
            if history and history[-1]["role"] == "user":
                history.pop()  # pertanyaan dikirim ulang lewat prompt augmentasi
            user_msg = None
        else:
            user_msg = Message(chat_id=chat_id, role="user", content=question)
            if attachment_ids:
                atts = s.exec(select(Document).where(Document.id.in_(attachment_ids))).all()
                user_msg.attachments = [{"document_id": d.id, "name": d.name, "ext": d.ext} for d in atts]
            if user_msg_id:
                user_msg.id = user_msg_id
            s.add(user_msg)
        asst = Message(chat_id=chat_id, role="assistant", status="complete", model=settings.chat_model)
        if asst_msg_id:
            asst.id = asst_msg_id
        s.add(asst)
        chat.updated_at = now()
        s.commit()
        s.refresh(asst)
        asst_id = asst.id
        title = chat.title
        threshold = settings.similarity_threshold
        top_k, model, system_prompt = settings.top_k, settings.chat_model, settings.system_prompt

    yield sse("meta", {"chat_id": chat_id, "assistant_message_id": asst_id, "title": title})

    skipped: list[str] = []
    if attachment_ids:
        waited = 0.0
        announced = False
        while waited < 120:
            with Session(engine) as s:
                atts = s.exec(select(Document).where(Document.id.in_(attachment_ids))).all()
            pending = [d.name for d in atts if d.status == "processing"]
            if not pending:
                skipped = [d.name for d in atts if d.status == "failed"]
                break
            if not announced:
                yield sse("waiting", {"documents": pending})
                announced = True
            await asyncio.sleep(0.5)
            waited += 0.5
        else:
            skipped = pending

    with Session(engine) as s:
        docs = {d.id: d.name for d in s.exec(select(Document).where(Document.status == "ready")).all()}
        enabled_ids = [d.id for d in s.exec(select(Document).where(Document.status == "ready", Document.enabled)).all()]

    try:
        hits = await asyncio.to_thread(vectorstore.search, question, top_k, enabled_ids)
    except Exception as e:  # Ollama mati dsb.
        msg = f"Gagal mengambil konteks: {e}"
        _finish(asst_id, msg, "error", [], None, True)
        yield sse("error", {"message": msg})
        return
    sources = [
        {**h, "document_name": docs.get(h["document_id"], "?")}
        for h in hits
        if h["score"] >= threshold
    ]
    # Pertanyaan lanjutan ("coba telaah lagi", "kok bisa?") nyaris tak punya makna sendiri sehingga skornya rendah.
    # Kalau retrieval kosong dan pertanyaannya pendek, pakai ulang potongan dari jawaban sebelumnya.
    if not sources and prev_sources and len(question.split()) <= FOLLOWUP_MAX_WORDS and FOLLOWUP_CUES.search(question):
        alive = {d for d in enabled_ids}
        sources = [{**s, "reused": True} for s in prev_sources if s.get("document_id") in alive]
    grounded = bool(sources)
    prompt = build_prompt(question, sources) if grounded else None
    yield sse("sources", {"sources": sources, "augmented_prompt": prompt, "all_hits": hits, "grounded": grounded, "skipped": skipped})

    # Tanpa konteks relevan, LLM tetap dipanggil dengan pertanyaan polos (jawaban dari pengetahuan model).
    # Mode umum memakai prompt singkat: model kecil cenderung ikut menulis "[1]" bila prompt menyebut sitasi.
    sys_msg = system_prompt if grounded else GENERAL_PROMPT
    messages = [{"role": "system", "content": sys_msg}, *history, {"role": "user", "content": prompt or question}]
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    cancel = threading.Event()

    def worker():
        try:
            for part in llm.client.chat(model=model, messages=messages, stream=True, options={"temperature": 0.2}):
                if cancel.is_set():
                    break
                loop.call_soon_threadsafe(queue.put_nowait, ("token", part.message.content))
            loop.call_soon_threadsafe(queue.put_nowait, ("end", None))
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, ("error", str(e)))

    threading.Thread(target=worker, daemon=True).start()
    answer = ""
    status = "complete"
    try:
        while True:
            kind, val = await queue.get()
            if kind == "token":
                answer += val
                yield sse("token", {"text": val})
            elif kind == "error":
                status = "error"
                answer = answer or f"Maaf, terjadi kesalahan saat menghubungi model: {val}"
                yield sse("error", {"message": answer})
                break
            else:
                break
    except (asyncio.CancelledError, GeneratorExit):
        status = "stopped"  # client menekan Stop / koneksi putus
        cancel.set()
        _finish(asst_id, answer, status, sources, prompt, grounded)
        raise
    cancel.set()
    _finish(asst_id, answer, status, sources, prompt, grounded)
    yield sse("done", {"status": status})


def _finish(asst_id: str, content: str, status: str, sources: list, prompt: str | None, grounded: bool):
    with Session(engine) as s:
        m = s.get(Message, asst_id)
        if m:
            m.content, m.status, m.sources, m.augmented_prompt, m.grounded = content, status, sources, prompt, grounded
            s.add(m)
            s.commit()

import hashlib
import mimetypes
import threading
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ..config import config
from ..db import engine, get_session
from ..models import AppSettings, Document, new_id
from ..schemas import DocumentPatch, TextDocument
from ..services import chunking, parsing, vectorstore

router = APIRouter(prefix="/documents", tags=["documents"])


def _out(d: Document) -> dict:
    return d.model_dump(exclude={"path", "sha256"})


def _friendly_error(e: Exception) -> str:
    """Pesan error parser (sering berbahasa Inggris/teknis) dibuat lebih ramah."""
    if isinstance(e, ValueError):
        return str(e)
    name = type(e).__name__
    if name in ("BadZipFile", "InvalidFileException", "XLRDError", "PdfReadError", "PackageNotFoundError"):
        return "File-nya rusak atau formatnya nggak sesuai ekstensinya. Coba simpan ulang lalu upload lagi."
    return f"Gagal memproses file ({name}). Coba upload ulang."


def _process(doc_id: str) -> None:
    """Parse -> chunk -> embed -> simpan. Jalan di thread background."""
    with Session(engine) as s:
        d = s.get(Document, doc_id)
        try:
            segments = parsing.parse_file(config.uploads_dir / d.path)
            chunks: list[tuple[str, int | None]] = []
            for text, page in segments:
                for c in chunking.chunk_text(text, config.chunk_size, config.chunk_overlap):
                    chunks.append((c, page))
            vectorstore.add_chunks(doc_id, chunks)
            d.chunk_count, d.status, d.error = len(chunks), "ready", None
        except Exception as e:
            vectorstore.delete_document(doc_id)
            d.status, d.error = "failed", _friendly_error(e)
        s.add(d)
        s.commit()


def _ingest(session: Session, filename: str, data: bytes, source: str) -> Document:
    ext = Path(filename).suffix.lower()
    if ext not in parsing.ALLOWED_EXT:
        raise HTTPException(415, "Format file tidak didukung. Pakai .txt, .md, .pdf, .docx, .xlsx, atau .csv.")
    limit = session.get(AppSettings, 1).max_file_size_mb
    if len(data) > limit * 1024 * 1024:
        raise HTTPException(413, f"Ukuran file melebihi batas {limit} MB.")
    if not data.strip():
        raise HTTPException(422, "File-nya kosong.")
    digest = hashlib.sha256(data).hexdigest()
    if session.exec(select(Document).where(Document.sha256 == digest)).first():
        raise HTTPException(409, "Dokumen ini sudah ada di memory.")
    doc_id = new_id()
    rel = f"{doc_id}{ext}"
    (config.uploads_dir / rel).write_bytes(data)
    doc = Document(
        id=doc_id, name=Path(filename).stem, original_filename=filename, ext=ext,
        size_bytes=len(data), sha256=digest, path=rel, source=source,
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    threading.Thread(target=_process, args=(doc_id,), daemon=True).start()
    return doc


@router.get("")
def list_documents(session: Session = Depends(get_session)):
    docs = session.exec(select(Document).order_by(Document.created_at.desc())).all()
    return [_out(d) for d in docs]


@router.post("", status_code=201)
async def upload(file: UploadFile, session: Session = Depends(get_session)):
    data = await file.read()
    return _out(_ingest(session, file.filename or "dokumen.txt", data, "file"))


@router.post("/text", status_code=201)
def add_text(body: TextDocument, session: Session = Depends(get_session)):
    return _out(_ingest(session, f"{body.title.strip()}.txt", body.content.encode(), "text"))


def _get(session: Session, doc_id: str) -> Document:
    d = session.get(Document, doc_id)
    if not d:
        raise HTTPException(404, "Dokumen tidak ditemukan.")
    return d


@router.patch("/{doc_id}")
def patch(doc_id: str, body: DocumentPatch, session: Session = Depends(get_session)):
    d = _get(session, doc_id)
    if body.enabled is not None:
        d.enabled = body.enabled
    if body.name:
        d.name = body.name
    session.add(d)
    session.commit()
    session.refresh(d)
    return _out(d)


@router.delete("/{doc_id}", status_code=204)
def delete(doc_id: str, session: Session = Depends(get_session)):
    d = _get(session, doc_id)
    vectorstore.delete_document(doc_id)
    (config.uploads_dir / d.path).unlink(missing_ok=True)
    session.delete(d)
    session.commit()


@router.get("/{doc_id}/file")
def file(doc_id: str, session: Session = Depends(get_session)):
    d = _get(session, doc_id)
    media = mimetypes.guess_type(d.original_filename)[0] or "application/octet-stream"
    return FileResponse(
        config.uploads_dir / d.path, media_type=media,
        headers={"Content-Disposition": f'inline; filename="{d.id}{d.ext}"'},
    )


@router.get("/{doc_id}/preview")
def preview(doc_id: str, session: Session = Depends(get_session)):
    d = _get(session, doc_id)
    path = config.uploads_dir / d.path
    base = {"id": d.id, "name": d.name, "ext": d.ext}
    if d.ext == ".pdf":
        return {**base, "kind": "pdf", "url": f"/api/documents/{d.id}/file"}
    if d.ext in (".txt", ".md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        return {**base, "kind": "markdown" if d.ext == ".md" else "text", "text": text}
    if d.ext == ".docx":
        segs = parsing.parse_file(path)
        return {**base, "kind": "text", "text": "\n\n".join(t for t, _ in segs)}
    # csv / xlsx -> tabel (maks 200 baris per sheet)
    import csv

    if d.ext == ".csv":
        with path.open(newline="", encoding="utf-8", errors="replace") as f:
            rows = [r for _, r in zip(range(201), csv.reader(f))]
        return {**base, "kind": "table", "sheets": [{"name": d.name, "rows": rows}]}
    sheets = [{"name": n, "rows": rows} for n, rows in parsing.read_sheets(path, max_rows=201)]
    return {**base, "kind": "table", "sheets": sheets}

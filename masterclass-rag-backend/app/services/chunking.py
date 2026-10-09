"""Chunking rekursif: paragraf -> baris -> kalimat -> karakter, dengan overlap."""
import re

SEPARATORS = ["\n\n", "\n", ". ", " "]


def _split(text: str, size: int, seps: list[str]) -> list[str]:
    if len(text) <= size:
        return [text]
    if not seps:
        return [text[i : i + size] for i in range(0, len(text), size)]
    sep, rest = seps[0], seps[1:]
    pieces = text.split(sep)
    out: list[str] = []
    for i, p in enumerate(pieces):
        p = p + (sep if i < len(pieces) - 1 and sep.strip() else "")
        out.extend(_split(p, size, rest) if len(p) > size else [p])
    return out


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        return []
    pieces = [p for p in _split(text, size, SEPARATORS) if p.strip()]
    chunks: list[str] = []
    cur = ""
    for p in pieces:
        if cur and len(cur) + len(p) + 1 > size:
            chunks.append(cur.strip())
            tail = cur[-overlap:] if overlap else ""
            # mulai chunk berikutnya dari batas kata agar overlap tidak memotong kata
            tail = tail[tail.find(" ") + 1 :] if " " in tail else tail
            cur = tail + "\n" + p if tail.strip() else p
        else:
            cur = f"{cur}\n{p}" if cur else p
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

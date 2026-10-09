import chromadb
import ollama

from ..config import config

_client = chromadb.PersistentClient(path=str(config.chroma_dir))
_collection = _client.get_or_create_collection("memory", metadata={"hnsw:space": "cosine"})
_ollama = ollama.Client(host=config.ollama_url)


def embed(texts: list[str], kind: str) -> list[list[float]]:
    """kind: 'document' atau 'query' (prefix wajib untuk nomic-embed-text)."""
    prefixed = [f"search_{kind}: {t}" for t in texts]
    return _ollama.embed(model=config.embed_model, input=prefixed).embeddings


def add_chunks(document_id: str, chunks: list[tuple[str, int | None]]) -> None:
    texts = [c[0] for c in chunks]
    batch = 16
    for i in range(0, len(texts), batch):
        part = texts[i : i + batch]
        _collection.add(
            ids=[f"{document_id}:{j}" for j in range(i, i + len(part))],
            documents=part,
            embeddings=embed(part, "document"),
            metadatas=[
                {"document_id": document_id, "chunk_index": j, "page": chunks[j][1] or 0}
                for j in range(i, i + len(part))
            ],
        )


def delete_document(document_id: str) -> None:
    _collection.delete(where={"document_id": document_id})


def search(question: str, top_k: int, document_ids: list[str]) -> list[dict]:
    if not document_ids:
        return []
    res = _collection.query(
        query_embeddings=embed([question], "query"),
        n_results=top_k,
        where={"document_id": {"$in": document_ids}},
    )
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append(
            {
                "document_id": meta["document_id"],
                "chunk_index": meta["chunk_index"],
                "page": meta["page"] or None,
                "text": doc,
                "score": round(1 - dist, 4),
            }
        )
    return out

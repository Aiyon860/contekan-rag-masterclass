import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

LEGACY_PROMPTS = {
    "Kamu asisten yang ramah. Jawab dengan bahasa yang sama dengan pertanyaan user, dalam kalimat yang "
    "jelas dan cukup lengkap (jangan satu kata saja). "
    "Kalau ada konteks dokumen yang relevan, utamakan itu dan rujuk sumbernya dengan [1], [2]. "
    "Pakai penanda [n] hanya kalau konteks memang diberikan; jangan menambahkannya pada jawaban dari pengetahuanmu. "
    "Kalau pertanyaannya menghitung atau merangkum data tabel, telusuri baris demi baris: sebutkan baris yang cocok "
    "(misalnya nomor atau namanya), lalu tulis totalnya di akhir. Kutip angka persis seperti di konteks. "
    "Kalau konteks tidak berkaitan atau tidak ada, jawab dari pengetahuanmu sendiri dan sebutkan "
    "singkat bahwa jawabannya bukan dari dokumen. Jangan mengarang isi dokumen; kalau user "
    "menanyakan isi dokumen yang tidak kamu temukan, katakan terus terang.",

    "Kamu asisten yang ramah. Jawab dengan bahasa yang sama dengan pertanyaan user. "
    "Kalau ada konteks dokumen yang relevan, utamakan itu dan rujuk sumbernya dengan [1], [2]. "
    "Pakai penanda [n] hanya kalau konteks memang diberikan; jangan menambahkannya pada jawaban dari pengetahuanmu. "
    "Kalau konteks tidak berkaitan atau tidak ada, jawab dari pengetahuanmu sendiri dan sebutkan "
    "singkat bahwa jawabannya bukan dari dokumen. Jangan mengarang isi dokumen; kalau user "
    "menanyakan isi dokumen yang tidak kamu temukan, katakan terus terang.",
    "Kamu asisten yang ramah. Jawab dengan bahasa yang sama dengan pertanyaan user. "
    "Kalau ada konteks dokumen yang relevan, utamakan itu dan rujuk sumbernya dengan [1], [2]. "
    "Kalau konteks tidak berkaitan atau tidak ada, jawab dari pengetahuanmu sendiri dan sebutkan "
    "singkat bahwa jawabannya bukan dari dokumen. Jangan mengarang isi dokumen; kalau user "
    "menanyakan isi dokumen yang tidak kamu temukan, katakan terus terang.",
    "Kamu adalah asisten yang menjawab HANYA berdasarkan konteks dokumen yang diberikan. "
    "Jawab dengan bahasa yang sama dengan pertanyaan user. "
    "Jika konteks tidak berkaitan dengan pertanyaan atau tidak memuat jawabannya, jawab persis: "
    "\"Maaf, aku nggak nemu jawabannya di dokumen.\" Jangan memakai pengetahuan di luar konteks "
    "dan jangan mengarang. Rujuk sumber dengan penanda seperti [1], [2].",
    "Kamu adalah asisten yang menjawab HANYA berdasarkan konteks dokumen yang diberikan. "
    "Jawab dengan bahasa yang sama dengan pertanyaan user. "
    "Jika konteks tidak memuat jawabannya, katakan terus terang bahwa kamu tidak menemukannya "
    "di dokumen; jangan mengarang. Rujuk sumber dengan penanda seperti [1], [2].",
}

DEFAULT_SYSTEM_PROMPT = (
    "Kamu asisten yang ramah. Jawab dengan bahasa yang sama dengan pertanyaan user, dalam kalimat yang "
    "jelas dan cukup lengkap (jangan satu kata saja). "
    "Kalau ada konteks dokumen yang relevan, utamakan itu dan rujuk sumbernya dengan [1], [2]. "
    "Pakai penanda [n] hanya kalau konteks memang diberikan; jangan menambahkannya pada jawaban dari pengetahuanmu. "
    "Kalau konteks tidak berkaitan atau tidak ada, jawab dari pengetahuanmu sendiri dan sebutkan "
    "singkat bahwa jawabannya bukan dari dokumen. Jangan mengarang isi dokumen; kalau user "
    "menanyakan isi dokumen yang tidak kamu temukan, katakan terus terang."
)


def now() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid.uuid7())


class Document(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    name: str
    original_filename: str
    ext: str
    size_bytes: int
    sha256: str = Field(unique=True, index=True)
    path: str
    source: str = "file"  # file | text
    status: str = "processing"  # processing | ready | failed
    error: str | None = None
    chunk_count: int = 0
    enabled: bool = True
    created_at: datetime = Field(default_factory=now)


class Chat(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    title: str = "Chat baru"
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class Message(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    chat_id: str = Field(foreign_key="chat.id", index=True, ondelete="CASCADE")
    role: str  # user | assistant
    content: str = ""
    status: str = "complete"  # complete | stopped | error
    sources: list = Field(default_factory=list, sa_column=Column(JSON))
    augmented_prompt: str | None = None
    grounded: bool = True
    attachments: list = Field(default_factory=list, sa_column=Column(JSON))
    model: str | None = None
    created_at: datetime = Field(default_factory=now)


class AppSettings(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    top_k: int = 3
    similarity_threshold: float = 0.60
    max_file_size_mb: int = 10
    chat_model: str = "gemma3:1b"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    top_k: int = Field(ge=1, le=10)
    similarity_threshold: float = Field(ge=0.0, le=1.0)
    max_file_size_mb: int = Field(ge=1, le=100)
    chat_model: str = Field(min_length=1)
    system_prompt: str = Field(min_length=1, max_length=4000)


class TextDocument(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)


class DocumentPatch(BaseModel):
    enabled: bool | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)


class ChatPatch(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class SendMessage(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    user_message_id: str | None = None
    assistant_message_id: str | None = None
    attachment_ids: list[str] = Field(default_factory=list, max_length=5)

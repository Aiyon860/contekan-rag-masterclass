from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text:latest"
    chunk_size: int = 800
    chunk_overlap: int = 100
    history_messages: int = 4

    data_dir: Path = BASE_DIR / "data"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'app.db'}"


config = Config()

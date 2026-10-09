import ollama

from ..config import config

client = ollama.Client(host=config.ollama_url)


def list_chat_models() -> list[str]:
    names = [m.model for m in client.list().models]
    embed = config.embed_model.split(":")[0]
    return [n for n in names if not n.startswith(embed) and "embed" not in n]

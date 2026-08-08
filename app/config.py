from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mistral_api_key: str | None = None
    mistral_chat_model: str = "mistral-small-latest"
    mistral_embed_model: str = "mistral-embed"
    rag_mode: str = "local"
    knowledge_base_dir: Path = Path("KnowledgeBase")
    local_index_path: Path = Path("storage/index.json")
    use_mistral_embeddings: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    # Optional Azure production settings (adapters fail clearly until provisioned)
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_chat_deployment: str | None = None
    azure_openai_embed_deployment: str | None = None
    azure_search_endpoint: str | None = None
    azure_search_api_key: str | None = None
    azure_search_index: str = "northwind-knowledge"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def require_mistral(self) -> str:
        if not self.mistral_api_key:
            raise RuntimeError("MISTRAL_API_KEY is required for answer generation.")
        return self.mistral_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()

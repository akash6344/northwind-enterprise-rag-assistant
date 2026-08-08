"""Azure OpenAI adapter stubs for production mode.

The local demo uses Mistral. These helpers document the production mapping and
fail clearly when Azure credentials are missing.
"""

from __future__ import annotations

from app.config import get_settings


class AzureOpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.endpoint = getattr(settings, "azure_openai_endpoint", None)
        self.api_key = getattr(settings, "azure_openai_api_key", None)
        self.chat_deployment = getattr(settings, "azure_openai_chat_deployment", None)
        self.embed_deployment = getattr(settings, "azure_openai_embed_deployment", None)
        if not all([self.endpoint, self.api_key, self.chat_deployment, self.embed_deployment]):
            raise RuntimeError(
                "Azure OpenAI is not configured. Set AZURE_OPENAI_ENDPOINT, "
                "AZURE_OPENAI_API_KEY, AZURE_OPENAI_CHAT_DEPLOYMENT, and "
                "AZURE_OPENAI_EMBED_DEPLOYMENT, or keep RAG_MODE=local."
            )

    def chat(self, messages: list[dict]) -> tuple[str, dict]:
        raise RuntimeError("Azure OpenAI chat adapter is documented for production; enable after provisioning.")

    def embeddings(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Azure OpenAI embeddings adapter is documented for production; enable after provisioning.")

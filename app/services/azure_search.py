"""Azure AI Search adapter stubs for production mode.

Local demo retrieval lives in LocalHybridIndex. This module documents the
production search contract and fails clearly when Azure Search is not configured.
"""

from __future__ import annotations

from app.config import get_settings


class AzureSearchClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.endpoint = getattr(settings, "azure_search_endpoint", None)
        self.api_key = getattr(settings, "azure_search_api_key", None)
        self.index_name = getattr(settings, "azure_search_index", "northwind-knowledge")
        if not all([self.endpoint, self.api_key]):
            raise RuntimeError(
                "Azure AI Search is not configured. Set AZURE_SEARCH_ENDPOINT and "
                "AZURE_SEARCH_API_KEY, or keep RAG_MODE=local."
            )

    def search(
        self,
        query: str,
        *,
        top_k: int = 6,
        filters: str | None = None,
        vector: list[float] | None = None,
    ) -> list[dict]:
        raise RuntimeError(
            "Azure AI Search hybrid/vector/semantic search adapter is documented for "
            "production; enable after provisioning the index schema in ingestion/index_schema.py."
        )

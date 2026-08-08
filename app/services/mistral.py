from __future__ import annotations

import requests


class MistralClient:
    def __init__(self, api_key: str, chat_model: str = "mistral-small-latest", embed_model: str = "mistral-embed"):
        self.api_key = api_key
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.base_url = "https://api.mistral.ai/v1"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict], temperature: float = 0.1, max_tokens: int = 700) -> tuple[str, dict]:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json={
                "model": self.chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"], payload.get("usage", {})

    def embeddings(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=self.headers,
            json={"model": self.embed_model, "input": texts},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return [item["embedding"] for item in payload["data"]]

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from hashlib import blake2b
from pathlib import Path

import numpy as np

TOKEN_RE = re.compile(r"[a-zA-Z0-9$%./+-]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def hash_embedding(text: str, dims: int = 384) -> list[float]:
    vector = np.zeros(dims, dtype=np.float32)
    for token in tokenize(text):
        digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        idx = value % dims
        sign = 1.0 if value & 1 else -1.0
        vector[idx] += sign
    norm = np.linalg.norm(vector)
    if norm:
        vector = vector / norm
    return vector.tolist()


class LocalHybridIndex:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.doc_freq: dict[str, int] = defaultdict(int)
        self.term_freqs: list[Counter] = []
        self.avg_doc_len = 1.0
        self._prepare()

    def _prepare(self) -> None:
        lengths = []
        for chunk in self.chunks:
            tokens = tokenize(chunk["content"])
            tf = Counter(tokens)
            self.term_freqs.append(tf)
            lengths.append(len(tokens))
            for term in tf:
                self.doc_freq[term] += 1
            if "embedding" not in chunk:
                chunk["embedding"] = hash_embedding(chunk["content"])
        self.avg_doc_len = sum(lengths) / max(1, len(lengths))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"chunks": self.chunks}, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "LocalHybridIndex":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data["chunks"])

    def _bm25(self, query_tokens: list[str], idx: int) -> float:
        tf = self.term_freqs[idx]
        doc_len = sum(tf.values())
        score = 0.0
        total_docs = max(1, len(self.chunks))
        k1 = 1.5
        b = 0.75
        for term in query_tokens:
            freq = tf.get(term, 0)
            if not freq:
                continue
            df = self.doc_freq.get(term, 0)
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            denom = freq + k1 * (1 - b + b * doc_len / self.avg_doc_len)
            score += idf * (freq * (k1 + 1) / denom)
        return score

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        va = np.array(a, dtype=np.float32)
        vb = np.array(b, dtype=np.float32)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        return float(np.dot(va, vb) / denom) if denom else 0.0

    def search(
        self,
        query: str,
        top_k: int = 6,
        improved: bool = True,
        department: str | None = None,
        access_groups: list[str] | None = None,
    ) -> list[dict]:
        query_tokens = tokenize(query)
        query_embedding = hash_embedding(query)
        access = set(access_groups or [])
        scored = []
        for idx, chunk in enumerate(self.chunks):
            if department and chunk.get("department") != department:
                continue
            if access and chunk.get("department") not in access:
                continue
            vector_score = self._cosine(query_embedding, chunk["embedding"])
            bm25_score = self._bm25(query_tokens, idx)
            current_boost = 0.08 if improved and chunk.get("is_current") else 0.0
            meta_text = " ".join(
                str(chunk.get(field) or "")
                for field in ("source_file", "title", "section", "document_id")
            ).lower()
            meta_hits = sum(1 for token in query_tokens if len(token) > 3 and token in meta_text)
            meta_boost = min(0.15, 0.04 * meta_hits) if improved else 0.0
            if improved:
                score = 0.55 * vector_score + 0.32 * min(1.0, bm25_score / 8.0) + current_boost + meta_boost
            else:
                score = vector_score
            scored.append(
                {
                    **chunk,
                    "score": round(float(score), 4),
                    "bm25_score": round(float(bm25_score), 4),
                    "vector_score": round(float(vector_score), 4),
                }
            )
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

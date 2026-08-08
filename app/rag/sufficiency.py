from __future__ import annotations

import re

STOPWORDS = {
    "what",
    "which",
    "when",
    "where",
    "who",
    "how",
    "many",
    "much",
    "does",
    "do",
    "did",
    "is",
    "are",
    "the",
    "a",
    "an",
    "for",
    "of",
    "to",
    "in",
    "on",
    "and",
    "or",
    "from",
    "with",
    "about",
    "customer",
    "customers",
    "company",
    "policy",
}


def _content_terms(question: str) -> set[str]:
    terms = {
        token.strip("?.!,").lower()
        for token in re.findall(r"[A-Za-z0-9$%./+-]+", question)
        if len(token) > 2 and token.lower() not in STOPWORDS
    }
    return terms


def evidence_confidence(chunks: list[dict]) -> float:
    if not chunks:
        return 0.0
    top = chunks[0].get("rerank_score", chunks[0].get("score", 0.0))
    supporting = sum(
        1
        for chunk in chunks[:5]
        if chunk.get("rerank_score", chunk.get("score", 0.0)) >= 0.22
    )
    return round(min(1.0, top * 1.05 + supporting * 0.07), 3)


def has_sufficient_evidence(question: str, chunks: list[dict]) -> bool:
    if not chunks:
        return False
    question_terms = _content_terms(question)
    if not question_terms:
        return False

    top_score = chunks[0].get("rerank_score", chunks[0].get("score", 0.0))
    content = " ".join(chunk.get("content", "").lower() for chunk in chunks[:4])
    overlap = sum(1 for term in question_terms if term in content)
    required = max(1, min(3, (len(question_terms) + 1) // 2))

    # Long distinctive terms must appear; avoids answering "refund" from unrelated pricing chunks.
    long_terms = {term for term in question_terms if len(term) >= 6}
    if long_terms and not all(term in content for term in long_terms):
        return False

    return top_score >= 0.22 and overlap >= required

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
    "should",
    "needed",
    "current",
    "above",
    "using",
    "please",
    "would",
    "could",
    "their",
    "there",
    "have",
    "has",
    "been",
    "into",
    "over",
    "under",
    "after",
    "before",
    "between",
    "receive",
    "employees",
    "employee",
}


def _content_terms(question: str) -> set[str]:
    terms = {
        token.strip("?.!,").lower()
        for token in re.findall(r"[A-Za-z0-9$%./+-]+", question)
        if len(token) > 2 and token.lower() not in STOPWORDS
    }
    return terms


def _normalize_term(term: str) -> str:
    """Lightweight singularization so 'leaves' matches 'leave' in policy text."""
    if len(term) > 4 and term.endswith("ies"):
        return term[:-3] + "y"
    if len(term) > 3 and term.endswith("ses"):
        return term[:-2]
    if len(term) > 3 and term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def _term_in_content(term: str, content: str) -> bool:
    variants = {term, _normalize_term(term)}
    return any(variant in content for variant in variants)


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
    overlap = sum(1 for term in question_terms if _term_in_content(term, content))
    required = max(1, min(3, (len(question_terms) + 1) // 2))

    # Distinctive long terms: require all when few; majority when many.
    long_terms = {term for term in question_terms if len(term) >= 6}
    if long_terms:
        present = sum(1 for term in long_terms if _term_in_content(term, content))
        needed = len(long_terms) if len(long_terms) <= 2 else max(1, (len(long_terms) + 1) // 2)
        if present < needed:
            return False

    return top_score >= 0.20 and overlap >= required

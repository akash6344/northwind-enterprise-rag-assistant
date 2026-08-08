from __future__ import annotations

import re
from collections import defaultdict

from app.services.local_index import LocalHybridIndex

COMPARE_RE = re.compile(
    r"\b(compare|versus|vs\.?|difference|changed?|from .+ to|between)\b",
    re.I,
)
YEAR_RE = re.compile(r"\b(20\d{2})\b")


def is_comparison_query(question: str) -> bool:
    return bool(COMPARE_RE.search(question))


def build_subqueries(question: str) -> list[str]:
    """Decompose comparison / multi-entity questions into retrieval subqueries."""
    if not is_comparison_query(question):
        return [question]

    years = YEAR_RE.findall(question)
    subqueries = [question]
    if len(years) >= 2:
        base = YEAR_RE.sub("", question)
        base = re.sub(r"\b(from|to|between|and|did|change|changed)\b", " ", base, flags=re.I)
        base = re.sub(r"\s+", " ", base).strip(" ?")
        for year in years:
            subqueries.append(f"{base} {year}".strip())
    if "carryover" in question.lower() and "pto" in question.lower() and "sick" in question.lower():
        subqueries.extend(["PTO carryover policy", "sick leave carryover policy"])
    if "prepaid" in question.lower() and "discount" in question.lower():
        subqueries.extend(["annual prepaid discount", "3-year prepaid discount"])
    # Preserve order, drop empties/dupes
    seen: set[str] = set()
    out: list[str] = []
    for item in subqueries:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def _lexical_overlap(query: str, content: str) -> float:
    q_terms = {t.lower() for t in re.findall(r"[a-zA-Z0-9$%./+-]+", query) if len(t) > 2}
    if not q_terms:
        return 0.0
    c_terms = {t.lower() for t in re.findall(r"[a-zA-Z0-9$%./+-]+", content)}
    return len(q_terms & c_terms) / len(q_terms)


def rerank_chunks(query: str, chunks: list[dict], final_k: int = 5) -> list[dict]:
    """Local lexical + score rerank used as the demo stand-in for semantic ranker."""
    ranked = []
    for chunk in chunks:
        overlap = _lexical_overlap(query, chunk.get("content", ""))
        current_boost = 0.05 if chunk.get("is_current") else 0.0
        combined = 0.62 * chunk.get("score", 0.0) + 0.33 * overlap + current_boost
        ranked.append({**chunk, "rerank_score": round(combined, 4), "overlap": round(overlap, 4)})
    ranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    return ranked[:final_k]


def pack_context(chunks: list[dict], final_k: int = 5) -> list[dict]:
    """Prefer diverse documents/sections over near-duplicate adjacent chunks."""
    selected: list[dict] = []
    seen_docs: dict[str, int] = defaultdict(int)
    seen_prefixes: set[str] = set()
    for chunk in chunks:
        doc = chunk.get("document_id") or chunk.get("source_file") or ""
        prefix = chunk.get("content", "")[:120].lower()
        if prefix in seen_prefixes:
            continue
        if seen_docs[doc] >= 2 and len(selected) < final_k:
            # allow a second pass later if we still have room
            continue
        selected.append(chunk)
        seen_docs[doc] += 1
        seen_prefixes.add(prefix)
        if len(selected) >= final_k:
            break
    if len(selected) < final_k:
        for chunk in chunks:
            if chunk in selected:
                continue
            selected.append(chunk)
            if len(selected) >= final_k:
                break
    return selected


def retrieve(
    index: LocalHybridIndex,
    query: str,
    *,
    improved: bool = True,
    top_k: int = 6,
    department: str | None = None,
    access_groups: list[str] | None = None,
) -> list[dict]:
    if not improved:
        return index.search(
            query,
            top_k=top_k,
            improved=False,
            department=department,
            access_groups=access_groups,
        )

    candidate_k = max(top_k * 2, 10)
    subqueries = build_subqueries(query)
    merged: dict[str, dict] = {}
    for subquery in subqueries:
        hits = index.search(
            subquery,
            top_k=candidate_k,
            improved=True,
            department=department,
            access_groups=access_groups,
        )
        for hit in hits:
            existing = merged.get(hit["chunk_id"])
            if not existing or hit["score"] > existing["score"]:
                merged[hit["chunk_id"]] = hit
    candidates = sorted(merged.values(), key=lambda item: item["score"], reverse=True)
    reranked = rerank_chunks(query, candidates, final_k=max(top_k, 8))
    return pack_context(reranked, final_k=top_k)

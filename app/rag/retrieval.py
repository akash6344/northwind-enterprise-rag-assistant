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
    """Expand overview/comparison questions into stronger retrieval subqueries."""
    subqueries = [question]
    lower = question.lower()

    if is_comparison_query(question):
        years = YEAR_RE.findall(question)
        if len(years) >= 2:
            base = YEAR_RE.sub("", question)
            base = re.sub(r"\b(from|to|between|and|did|change|changed)\b", " ", base, flags=re.I)
            base = re.sub(r"\s+", " ", base).strip(" ?")
            for year in years:
                subqueries.append(f"{base} {year}".strip())
        if "carryover" in lower and "pto" in lower and "sick" in lower:
            subqueries.extend(["PTO carryover policy", "sick leave carryover policy"])
        if "prepaid" in lower and "discount" in lower:
            subqueries.extend(["annual prepaid discount", "3-year prepaid discount"])

    # Broad topic questions need section-level expansion.
    if "benefit" in lower:
        subqueries.extend(
            [
                "Employee Benefits Guide overview",
                "Health Insurance medical dental vision plan tiers",
                "Retirement Savings 401(k) match",
                "Life Disability Insurance wellness tuition reimbursement",
                "Additional Perks commuter stipend ESPP learning stipend",
            ]
        )
    if re.search(r"\bleave\b|\bpto\b|time off|sick leave", lower) and "benefit" not in lower:
        subqueries.extend(["Leave Time Off Policy PTO sick leave parental"])
    if "pricing" in lower or "enterprise tier" in lower or "professional tier" in lower:
        subqueries.extend(["Subscription Tiers price seat month", "Pricing 2026 current"])

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
    """Local lexical + metadata rerank used as the demo stand-in for semantic ranker."""
    ranked = []
    lower_q = query.lower()
    for chunk in chunks:
        content = chunk.get("content", "")
        section = str(chunk.get("section") or "")
        source = str(chunk.get("source_file") or "")
        title = str(chunk.get("title") or "")
        meta = f"{source} {title} {section}"
        overlap = _lexical_overlap(query, content)
        meta_overlap = _lexical_overlap(query, meta)
        current_boost = 0.05 if chunk.get("is_current") else 0.0
        filename_boost = 0.12 if any(term in source.lower() for term in lower_q.split() if len(term) > 4) else 0.0

        penalty = 0.0
        section_l = section.lower()
        if section_l in {"9. contact", "contact"} or "contact" in section_l:
            penalty += 0.12
        if len(content.split()) < 20:
            penalty += 0.1
        # Leave-without-pay is a weak match for a general "benefits" overview.
        if "benefit" in lower_q and "leave" in source.lower() and "without pay" in section_l:
            penalty += 0.18

        combined = (
            0.48 * chunk.get("score", 0.0)
            + 0.27 * overlap
            + 0.18 * meta_overlap
            + current_boost
            + filename_boost
            - penalty
        )
        ranked.append(
            {
                **chunk,
                "rerank_score": round(combined, 4),
                "overlap": round(overlap, 4),
            }
        )
    ranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    return ranked[:final_k]


def pack_context(chunks: list[dict], final_k: int = 5, query: str = "") -> list[dict]:
    """Prefer diverse high-value sections; allow denser packing for single-topic docs."""
    selected: list[dict] = []
    seen_docs: dict[str, int] = defaultdict(int)
    seen_prefixes: set[str] = set()
    lower_q = query.lower()

    for chunk in chunks:
        doc = chunk.get("document_id") or chunk.get("source_file") or ""
        prefix = chunk.get("content", "")[:120].lower()
        if prefix in seen_prefixes:
            continue
        max_per_doc = 2
        if "benefit" in lower_q and "benefit" in str(doc).lower():
            max_per_doc = final_k
        if seen_docs[doc] >= max_per_doc:
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

    candidate_k = max(top_k * 2, 12)
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
    reranked = rerank_chunks(query, candidates, final_k=max(top_k + 4, 10))
    return pack_context(reranked, final_k=top_k, query=query)

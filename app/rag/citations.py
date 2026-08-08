import re
from pathlib import Path

from app.models import Citation

CHUNK_ID_RE = re.compile(r"\s*\[(?:[a-f0-9]{12}|Source:[^\]]+)\]", re.I)


def clean_answer_text(answer: str) -> str:
    """Remove leftover technical citation markers from model output."""
    cleaned = CHUNK_ID_RE.sub("", answer)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    return cleaned.strip()


def extract_citations(answer: str, chunks: list[dict]) -> list[Citation]:
    cited_ids = set(re.findall(r"\[([a-f0-9]{12})\]", answer))
    source_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    selected = cited_ids or {chunk["chunk_id"] for chunk in chunks[:3]}
    citations = []
    for chunk_id in selected:
        chunk = source_by_id.get(chunk_id)
        if not chunk:
            continue
        citations.append(
            Citation(
                chunk_id=chunk["chunk_id"],
                source_file=chunk["source_file"],
                department=chunk["department"],
                section=chunk.get("section"),
                page=chunk.get("page"),
                score=chunk.get("score", 0.0),
            )
        )
    return citations


def format_source_label(source_file: str, section: str | None = None, page: int | None = None) -> str:
    name = Path(source_file).name
    parts = [name]
    if section:
        parts.append(section)
    if page is not None:
        parts.append(f"p.{page}")
    return " · ".join(parts)

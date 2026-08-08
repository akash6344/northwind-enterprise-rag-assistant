import re

from app.models import Citation


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

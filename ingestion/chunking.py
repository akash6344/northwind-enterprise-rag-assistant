import re
from hashlib import sha1


SECTION_RE = re.compile(r"(?m)^(\d+(?:\.\d+)*\.?\s+[^\n]+)$")


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def split_sections(text: str) -> list[tuple[str | None, str]]:
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return [(None, text)]
    sections = []
    if matches[0].start() > 0:
        sections.append((None, text[: matches[0].start()].strip()))
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[start:end].strip()))
    return [(section, body) for section, body in sections if body]


def window_text(text: str, max_tokens: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    chunks = []
    step = max(1, max_tokens - overlap)
    for start in range(0, len(words), step):
        window = words[start : start + max_tokens]
        if window:
            chunks.append(" ".join(window))
        if start + max_tokens >= len(words):
            break
    return chunks


def make_chunks(records: list[dict], max_tokens: int = 850, overlap: int = 120) -> list[dict]:
    chunks: list[dict] = []
    for record in records:
        for section, body in split_sections(record["text"]):
            for part_idx, text in enumerate(window_text(body, max_tokens=max_tokens, overlap=overlap), start=1):
                digest = sha1(f"{record['source_file']}:{record.get('page')}:{section}:{part_idx}:{text[:80]}".encode()).hexdigest()[:12]
                chunks.append({
                    **{k: v for k, v in record.items() if k != "text"},
                    "chunk_id": digest,
                    "section": section or record.get("sheet") or "Document overview",
                    "content": text,
                    "token_estimate": estimate_tokens(text),
                })
    return chunks

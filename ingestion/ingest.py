from pathlib import Path

from app.config import get_settings
from app.services.local_index import LocalHybridIndex
from ingestion.chunking import make_chunks
from ingestion.parsing import parse_knowledge_base


def build_index() -> int:
    settings = get_settings()
    records = parse_knowledge_base(Path(settings.knowledge_base_dir))
    chunks = make_chunks(records)
    index = LocalHybridIndex(chunks)
    index.save(Path(settings.local_index_path))
    return len(chunks)


if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} chunks.")

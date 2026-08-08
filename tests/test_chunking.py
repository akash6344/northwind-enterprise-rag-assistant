from ingestion.chunking import make_chunks


def test_make_chunks_preserves_metadata():
    chunks = make_chunks([
        {
            "source_file": "KnowledgeBase/HR/Test.pdf",
            "department": "HR",
            "title": "Policy",
            "document_id": "test",
            "document_type": "pdf",
            "version": "1.0",
            "effective_date": "January 1, 2026",
            "supersedes": None,
            "is_current": True,
            "access_groups": ["HR"],
            "page": 1,
            "text": "1. Purpose\nThis is a test policy.",
        }
    ])
    assert chunks
    assert chunks[0]["department"] == "HR"
    assert chunks[0]["section"] == "1. Purpose"

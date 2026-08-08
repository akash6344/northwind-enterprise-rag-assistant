from app.rag.retrieval import build_subqueries, pack_context, retrieve
from app.services.local_index import LocalHybridIndex


def test_build_subqueries_for_year_comparison():
    subs = build_subqueries("Did Professional API limits change from 2025 to 2026?")
    assert any("2025" in item for item in subs)
    assert any("2026" in item for item in subs)


def test_pack_context_diversifies_documents():
    chunks = [
        {"chunk_id": "1", "document_id": "a", "content": "alpha one", "score": 0.9},
        {"chunk_id": "2", "document_id": "a", "content": "alpha two", "score": 0.8},
        {"chunk_id": "3", "document_id": "a", "content": "alpha three", "score": 0.7},
        {"chunk_id": "4", "document_id": "b", "content": "beta one", "score": 0.6},
    ]
    packed = pack_context(chunks, final_k=3)
    docs = [chunk["document_id"] for chunk in packed]
    assert "b" in docs


def test_retrieve_improved_returns_results():
    index = LocalHybridIndex(
        [
            {
                "chunk_id": "x1",
                "content": "Enterprise tier price is 199 per seat per month",
                "department": "Sales",
                "source_file": "pricing.pdf",
                "document_id": "pricing2026",
                "section": "Subscription Tiers",
                "is_current": True,
            }
        ]
    )
    hits = retrieve(index, "current Enterprise tier price", improved=True, access_groups=["Sales"], top_k=3)
    assert hits
    assert hits[0]["chunk_id"] == "x1"

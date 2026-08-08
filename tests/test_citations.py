from app.models import Citation
from app.rag.citations import clean_answer_text, extract_citations


def test_extract_citations_prefers_answer_ids():
    chunks = [
        {
            "chunk_id": "aaaaaaaaaaaa",
            "source_file": "a.pdf",
            "department": "Sales",
            "section": "Tiers",
            "page": 1,
            "score": 0.9,
        },
        {
            "chunk_id": "bbbbbbbbbbbb",
            "source_file": "b.pdf",
            "department": "Sales",
            "section": "Tiers",
            "page": 2,
            "score": 0.8,
        },
    ]
    citations = extract_citations("The price is $99 [aaaaaaaaaaaa].", chunks)
    assert len(citations) == 1
    assert isinstance(citations[0], Citation)
    assert citations[0].chunk_id == "aaaaaaaaaaaa"


def test_extract_citations_falls_back_to_top_chunks():
    chunks = [
        {
            "chunk_id": "cccccccccccc",
            "source_file": "c.pdf",
            "department": "HR",
            "section": "Leave",
            "page": 1,
            "score": 0.7,
        }
    ]
    citations = extract_citations("Employees receive sick leave.", chunks)
    assert citations[0].chunk_id == "cccccccccccc"


def test_clean_answer_text_strips_chunk_ids():
    text = "Employees get 10 sick days [aa0de3298232]."
    assert clean_answer_text(text) == "Employees get 10 sick days."

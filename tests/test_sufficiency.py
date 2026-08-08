from app.rag.sufficiency import evidence_confidence, has_sufficient_evidence


def test_insufficient_when_key_term_missing():
    chunks = [
        {
            "content": "Subscription pricing for Standard and Professional tiers.",
            "score": 0.55,
            "rerank_score": 0.55,
        }
    ]
    assert not has_sufficient_evidence("What is the refund policy for Standard customers?", chunks)


def test_sufficient_when_overlap_and_score_ok():
    chunks = [
        {
            "content": "Employees receive 10 paid sick leave days each calendar year.",
            "score": 0.5,
            "rerank_score": 0.5,
        }
    ]
    assert has_sufficient_evidence("How many paid sick leave days do employees receive?", chunks)


def test_confidence_zero_without_chunks():
    assert evidence_confidence([]) == 0.0

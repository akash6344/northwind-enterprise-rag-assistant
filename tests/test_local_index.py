from app.services.local_index import LocalHybridIndex


def test_access_filter_blocks_department():
    index = LocalHybridIndex([
        {
            "chunk_id": "a",
            "content": "HR benefits include retirement match",
            "department": "HR",
            "source_file": "hr.pdf",
            "section": "Benefits",
            "is_current": True,
        }
    ])
    assert index.search("retirement match", access_groups=["Engineering"]) == []

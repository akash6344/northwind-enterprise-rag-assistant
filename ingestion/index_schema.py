"""Azure AI Search index schema for production mode.

This schema mirrors the local chunk metadata used by the demo index so the
same ingestion pipeline can target Azure AI Search without redesigning fields.
"""

AZURE_SEARCH_INDEX_SCHEMA = {
    "name": "northwind-knowledge",
    "fields": [
        {"name": "chunk_id", "type": "Edm.String", "key": True, "filterable": True},
        {"name": "document_id", "type": "Edm.String", "filterable": True, "facetable": True},
        {"name": "source_file", "type": "Edm.String", "filterable": True},
        {"name": "department", "type": "Edm.String", "filterable": True, "facetable": True},
        {"name": "title", "type": "Edm.String", "searchable": True},
        {"name": "document_type", "type": "Edm.String", "filterable": True},
        {"name": "section", "type": "Edm.String", "searchable": True, "filterable": True},
        {"name": "page", "type": "Edm.Int32", "filterable": True},
        {"name": "version", "type": "Edm.String", "filterable": True},
        {"name": "effective_date", "type": "Edm.String", "filterable": True},
        {"name": "supersedes", "type": "Edm.String", "filterable": True},
        {"name": "is_current", "type": "Edm.Boolean", "filterable": True},
        {"name": "access_groups", "type": "Collection(Edm.String)", "filterable": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {
            "name": "content_vector",
            "type": "Collection(Edm.Single)",
            "searchable": True,
            "dimensions": 1536,
            "vectorSearchProfile": "default-vector-profile",
        },
    ],
    "semantic": {
        "configurations": [
            {
                "name": "default-semantic",
                "prioritizedFields": {
                    "titleField": {"fieldName": "title"},
                    "contentFields": [{"fieldName": "content"}],
                    "keywordsFields": [{"fieldName": "section"}, {"fieldName": "department"}],
                },
            }
        ]
    },
    "security_filter_example": "access_groups/any(g: search.in(g, 'HR|Finance')) and is_current eq true",
}

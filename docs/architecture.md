# Production Architecture

The working demo runs with Mistral and a local hybrid index to control cost. The production design maps the same pipeline onto Azure services without changing the RAG control flow.

## Service mapping

| Demo component | Production Azure component |
| --- | --- |
| `KnowledgeBase/` files | Azure Blob Storage |
| `python -m ingestion.ingest` | Event Grid + Azure Functions / Container Apps ingestion worker |
| Local hash embeddings / optional Mistral embeddings | Azure OpenAI embeddings |
| `LocalHybridIndex` BM25 + vector | Azure AI Search hybrid vector + keyword retrieval |
| Local lexical rerank | Azure AI Search semantic ranker |
| Mistral chat | Azure OpenAI chat deployment |
| FastAPI + Streamlit | App Service or Container Apps |
| Sidebar access groups | Microsoft Entra ID claims mapped to search filters |
| `.env` secrets | Key Vault + Managed Identity |
| Structured JSON logs | Application Insights traces/metrics |

## Ingestion path

1. Documents land in Blob Storage under department prefixes.
2. Event Grid triggers the ingestion worker.
3. Worker parses PDF/DOCX/XLSX, extracts section-aware chunks, and stores metadata (`department`, `version`, `effective_date`, `is_current`, `access_groups`).
4. Worker embeds content with Azure OpenAI and upserts into Azure AI Search using `ingestion/index_schema.py`.
5. Optional Document Intelligence handles scanned/table-heavy PDFs.

## Query path

1. User authenticates with Entra ID.
2. API rewrites follow-ups, classifies ambiguity, and builds metadata filters from claims.
3. Azure AI Search runs hybrid retrieval with security filters applied before ranking.
4. Semantic ranker selects the final evidence set.
5. Azure OpenAI generates a grounded answer with citations.
6. Application Insights records request ID, retrieve/generate latency, token usage, and citation IDs.

## Security and isolation

- ACL metadata is attached at ingestion time.
- Access filters run in search, never only in the prompt.
- Private endpoints and Managed Identity protect OpenAI, Search, and storage.
- Logs keep citation IDs and metadata; avoid shipping full sensitive context when unnecessary.

## Scale and cost

- ~10k documents: one search index, scheduled/event-driven ingestion, hybrid retrieval.
- Millions of documents: partition by tenant/domain, incremental indexing, stricter filters, offline evaluation, and lifecycle management.
- Cost controls: rerank/pack context before generation, smaller models for rewrite/classification, batch embeddings, cache stable answers where policy allows.

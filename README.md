# Northwind Enterprise Knowledge Assistant

Author: Akash Uppala

This is a cost-controlled RAG assignment implementation. The working demo uses Mistral for answer generation and a local hybrid retrieval index. The production architecture maps the same design to Azure OpenAI, Azure AI Search, Blob Storage, Entra ID, Key Vault, and Application Insights.

## Features

- PDF, DOCX, and XLSX ingestion with section-aware chunking
- Metadata-rich chunks: department, version, effective date, source, page, section, access groups
- Baseline vector-only retrieval
- Improved hybrid retrieval: BM25 + vector, current-document boost, multi-query expansion, lexical rerank, context packing
- Ambiguity clarification, evidence sufficiency checks, grounded answers with citations
- Department access filtering before generation
- FastAPI API + minimal Streamlit UI + Docker
- Baseline vs improved evaluation reports

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Mistral key to `.env`:

```bash
MISTRAL_API_KEY=...
```

## Build The Local Index

```bash
python -m ingestion.ingest
```

## Run API

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Ask a question:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the current Enterprise tier price?","access_groups":["Sales"],"improved":true}'
```

Security note: Mistral generation sends the selected retrieved chunks to the Mistral API. Do not use confidential data unless that external processing is acceptable for your submission/demo context.

## Run UI

```bash
streamlit run streamlit_ui/app.py
```

## Docker

```bash
docker compose up --build
```

Then open:

- API: http://localhost:8000
- UI: http://localhost:8501

## Evaluation

Retrieval-only baseline vs improved comparison (no LLM cost):

```bash
python -m evaluation.run_eval --retrieval-only
```

Full answer evaluation (calls Mistral):

```bash
python -m evaluation.run_eval
```

Reports written to:

- `evaluation/results/baseline.md`
- `evaluation/results/improved.md`
- `evaluation/results/comparison.md`
- `evaluation/results/eval_results.json`

## Failure scenarios covered

1. Correct document, wrong chunk -> hybrid retrieval + rerank + section metadata
2. Multi-section / multi-document questions -> multi-query retrieval + context packing
3. Conflicting versions -> `is_current` / effective-date aware ranking
4. Missing information -> sufficiency checks and grounded refusal
5. Ambiguous queries -> clarification instead of guessing
6. Conversational follow-ups -> query rewriting from recent history
7. Access control -> department filters before generation

## Docs

- `docs/architecture.md`
- `docs/architecture-diagram.mmd`
- `docs/problem-solving.md`
- `docs/demo-script.md`
- `ASSIGNMENT_PLAN.md`

## Azure Production Mapping

In production, local retrieval maps to Azure AI Search hybrid/vector/semantic retrieval, Mistral maps to Azure OpenAI, local files map to Blob Storage, and local metadata filters map to Entra ID claim-based ACL filters. Adapter stubs and the search schema live in:

- `app/services/azure_openai.py`
- `app/services/azure_search.py`
- `ingestion/index_schema.py`

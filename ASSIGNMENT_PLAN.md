# Senior AI Engineer Azure RAG Assignment Plan

## 1. Assignment Interpretation

The assignment asks for a working RAG-based Enterprise Knowledge Assistant using the Microsoft Azure AI stack. The expected submission is not just a chatbot. It must demonstrate senior-level architecture judgment, retrieval debugging, objective evaluation, and production-readiness thinking.

Core deliverables:

- Python RAG application with API or simple UI
- Document ingestion pipeline
- Azure AI Search integration
- Azure OpenAI integration
- Retrieval, reranking, grounded answer generation, and citations
- Evaluation dataset and baseline vs improved results
- Production Azure architecture diagram
- README or presentation answers for architecture and problem-solving questions
- 5-minute demo and architecture video

The strongest submission should make it obvious how the system behaves before and after improvements, why failures happen, and how each design choice improves retrieval, grounding, security, latency, or cost.

## 2. Recommended Technical Direction

Use a pragmatic Python-first implementation with two runtime modes:

- Backend/API: FastAPI
- Ingestion CLI: Python command-line script
- Parsing: PDF/text parser with normalized document metadata
- Chunking: configurable section-aware chunking with overlap
- Demo mode embeddings: local sentence-transformer embeddings, or Mistral embeddings if the available API key supports them
- Demo mode index: local FAISS/Chroma vector index plus BM25 keyword index
- Demo mode generation: Mistral chat/completion API with strict grounded-answer prompt
- Production mode embeddings: Azure OpenAI embeddings
- Production mode index: Azure AI Search with vector fields, text fields, metadata fields, and semantic configuration
- Retrieval: hybrid search as the improved path in both modes
- Reranking: local cross-encoder or Mistral-based rerank in demo mode; Azure AI Search semantic ranker in production mode
- Evaluation: local Python evaluation scripts plus exported JSON/Markdown results
- Observability: structured logs, request IDs, latency breakdowns, token usage, and Application Insights design notes

Keep the UI minimal. A FastAPI endpoint plus a small Streamlit or HTML chat page is enough. The evaluation and debugging evidence matter more than frontend polish.

Cost-control position:

- The assignment recommends Azure services, but does not explicitly require paid Azure execution for every demo step.
- The working demo can run locally using Mistral and local retrieval.
- The README must clearly state that the implementation is provider-pluggable and includes an Azure production architecture/adapters.
- The architecture diagram should still show the Azure deployment requested by the assignment.
- If Azure is not used live, the demo video should say this was a cost-controlled local implementation of the same RAG design, with Azure service mappings documented.

## 3. Repository Structure

Proposed structure:

```text
rag-assignment/
  app/
    api.py
    config.py
    models.py
    rag/
      answer.py
      citations.py
      prompts.py
      retrieval.py
      query_rewrite.py
      sufficiency.py
    services/
      azure_openai.py
      azure_search.py
      mistral.py
      local_index.py
      telemetry.py
  ingestion/
    ingest.py
    parsing.py
    chunking.py
    metadata.py
    index_schema.py
  evaluation/
    dataset.yaml
    run_eval.py
    metrics.py
    results/
      baseline.md
      improved.md
      comparison.md
  docs/
    architecture.md
    architecture-diagram.mmd
    problem-solving.md
    demo-script.md
  data/
    raw/
    processed/
  tests/
    test_chunking.py
    test_citations.py
    test_sufficiency.py
  README.md
  .env.example
  requirements.txt
```

## 4. Implementation Phases

### Phase 1: Foundation

Goal: Make the project runnable and explainable.

Tasks:

- Create Python project skeleton.
- Add `.env.example` for `RAG_MODE=local|azure`, Mistral settings, and optional Azure settings.
- Define configuration loading with explicit required variables.
- Add README setup instructions.
- Add a basic health endpoint.
- Add logging with request ID and elapsed time fields.

Acceptance criteria:

- A reviewer can install dependencies, configure environment variables, and start the API.
- Missing provider configuration fails clearly.
- The README explains the execution path at a high level.

### Phase 2: Ingestion Pipeline

Goal: Convert enterprise documents into searchable indexed chunks.

Tasks:

- Parse PDF/text documents from `data/raw`.
- Normalize metadata: `document_id`, `title`, `source_path`, `department`, `version`, `effective_date`, `section`, `page`, `chunk_id`.
- Implement section-aware chunking with configurable size and overlap.
- Generate embeddings using local embeddings or Mistral in demo mode.
- Build a local vector/BM25 index in demo mode.
- Keep the Azure AI Search schema documented and optionally implemented behind `RAG_MODE=azure`.

Recommended defaults:

- Chunk size: 700-1,000 tokens
- Overlap: 100-150 tokens
- Top-K baseline: 5
- Top-K improved: 8-12 before reranking, 4-6 after reranking

Acceptance criteria:

- Ingestion can be rerun safely.
- Indexed documents include citations metadata.
- Chunking settings are visible and reproducible.

### Phase 3: Baseline RAG

Goal: Build the simplest working RAG path before optimization.

Tasks:

- Implement user query endpoint.
- Embed query.
- Run vector search against the selected retrieval provider.
- Build answer context from retrieved chunks.
- Generate grounded answer with citations.
- Return answer, citations, retrieved chunks, latency, and token usage.

Baseline constraints:

- No query rewriting.
- No hybrid search.
- No reranking.
- Minimal sufficiency checks.

Acceptance criteria:

- The chatbot answers straightforward questions with citations.
- The evaluation script can run against the baseline.
- Baseline weaknesses are observable, not hidden.

### Phase 4: Improved RAG

Goal: Address the assignment's failure scenarios with specific improvements.

Improvements:

- Hybrid retrieval: combine keyword/BM25 and vector search.
- Semantic ranker/reranker: improve chunk ordering and reduce irrelevant context.
- Query rewriting: rewrite conversational or vague follow-ups into standalone retrieval queries.
- Metadata filtering: prefer current documents, effective dates, departments, and user access scope.
- Multi-query retrieval: decompose comparison questions into subqueries when needed.
- Context packing: include diverse, high-value chunks instead of adjacent duplicates.
- Sufficiency scoring: detect weak evidence before answering.
- Citation validation: cite only chunks actually used in the answer.

Acceptance criteria:

- Each improvement maps to at least one measured failure mode.
- The improved path can be toggled from the baseline for evaluation.
- The system refuses or asks clarification when evidence is missing or ambiguous.

## 5. Failure Scenario Strategy

### Scenario 1: Correct Document, Wrong Chunk

Likely causes:

- Chunk too large or too small
- Missing section metadata
- Pure vector search missing exact terms
- Top-K too low
- No reranking

Solution:

- Use section-aware chunking.
- Add hybrid search.
- Increase candidate Top-K before reranking.
- Use semantic reranking.
- Track retrieval hit rate by expected document and section.

### Scenario 2: Information Across Multiple Sections

Likely causes:

- Single-query retrieval returns only one side of comparison.
- Context packing removes useful secondary chunks.

Solution:

- Detect comparison intent.
- Generate subqueries for each entity being compared.
- Retrieve candidates per subquery.
- Deduplicate and pack context by entity and section.
- Ask the LLM to produce a structured comparison grounded in retrieved chunks.

### Scenario 3: Similar Documents or Conflicting Information

Likely causes:

- Older and newer documents have similar embeddings.
- No version or effective-date ranking.

Solution:

- Store `version`, `effective_date`, and `is_current` metadata.
- Filter to current documents by default.
- If multiple versions are relevant, cite the newest and mention version scope.
- Add tests where `Leave_Policy_2024.pdf` and `Leave_Policy_2026.pdf` conflict.

### Scenario 4: Hallucination or Missing Information

Likely causes:

- Prompt allows unsupported synthesis.
- Retrieved chunks are weak but still passed to generation.

Solution:

- Add retrieval confidence checks using score thresholds, chunk agreement, and citation coverage.
- Prompt the model to answer only from provided context.
- Return "I do not have enough information in the provided documents" when evidence is insufficient.
- Measure hallucination rate in evaluation.

### Scenario 5: Ambiguous Query

Likely causes:

- Query lacks entity, policy, department, or prior context.

Solution:

- If conversation context resolves the query, rewrite it into a standalone question.
- If multiple plausible interpretations remain, ask a clarification question.
- Do not guess when retrieved chunks point to different meanings of "limit."

### Scenario 6: Conversational Context

Likely causes:

- Full chat history pollutes retrieval.
- Follow-up questions are embedded without necessary context.

Solution:

- Maintain compact conversation state with entities, document scope, and last confirmed topic.
- Rewrite follow-ups into standalone retrieval queries.
- Use recent turns for interpretation, not as raw retrieval context.
- Keep answer generation context limited to retrieved document chunks.

## 6. Evaluation Plan

Create `evaluation/dataset.yaml` with approximately 20-30 cases:

- Straightforward factual questions
- Section-specific questions
- Multi-document comparison questions
- Version-conflict questions
- Ambiguous questions
- No-answer questions
- Conversational follow-ups

Each item should include:

- `question`
- `expected_answer`
- `expected_document`
- `expected_section`
- `difficulty`
- `type`
- optional `conversation_history`

Metrics:

- Retrieval hit rate: expected document appears in Top-K.
- Section hit rate: expected section appears in Top-K.
- Mean reciprocal rank: expected chunk appears higher after improvement.
- Relevance rating: 0-2 score per retrieved chunk.
- Answer correctness: 0-2 manual or evaluator-assisted score.
- Groundedness: answer claims are supported by citations.
- Citation correctness: cited chunks contain the supporting evidence.
- Hallucination rate: no-answer questions that produce fabricated answers.
- Latency: end-to-end, retrieval, rerank, generation.
- Cost estimate: input tokens, output tokens, embedding calls, search calls.

Required report:

```text
Baseline RAG
  -> failures observed
Improved RAG
  -> changes applied
Comparison
  -> metric deltas and explanation
```

## 7. Production Architecture Plan

Production components:

- Azure Blob Storage for raw and processed documents.
- Event Grid to trigger ingestion when documents are uploaded.
- Azure Functions or Container Apps for ingestion workers.
- Azure AI Document Intelligence if complex PDFs, tables, or scanned documents are included.
- Azure OpenAI for embeddings and answer generation.
- Azure AI Search for hybrid/vector/semantic retrieval.
- FastAPI application on Azure App Service or Azure Container Apps.
- Microsoft Entra ID for user authentication.
- Azure Key Vault for secrets.
- Managed Identity for service-to-service access.
- Application Insights for logs, traces, latency, errors, and token usage.
- Azure API Management if external enterprise API governance is needed.

Security and isolation:

- Add department, ACL, tenant, and sensitivity metadata at ingestion time.
- Apply security filters in Azure AI Search before retrieval.
- Never rely only on prompt instructions for document access control.
- Use private endpoints and network restrictions for production.
- Log citation IDs and metadata, not sensitive full context, where possible.

Scale strategy:

- For 10,000 documents: single Azure AI Search index, scheduled ingestion, straightforward hybrid retrieval.
- For 5-10 million documents: partition by tenant/domain, asynchronous ingestion, index lifecycle management, sharding strategy, cached embeddings, incremental updates, stricter metadata filters, and offline quality monitoring.

Cost strategy:

- Reduce prompt context with reranking and context packing.
- Cache repeated query results and stable answers where allowed.
- Use smaller models for rewriting and classification.
- Batch embeddings during ingestion.
- Track token usage per endpoint, user, department, and document set.

## 8. Problem-Solving Answers To Include

The README or `docs/problem-solving.md` should explicitly answer:

- How to debug low retrieval quality when only one of five chunks is relevant.
- How to debug response latency increasing from 3 seconds to 12 seconds.
- How architecture changes from 10,000 to 5 million documents.
- How to enforce department-level access control for HR, Finance, Legal, and Engineering.
- How to investigate and reduce Azure OpenAI cost spikes.
- How to debug wrong answers with valid-looking citations from query through retrieval, ranking, context, prompt, model output, and citation assembly.

These answers should reference the implementation choices and evaluation evidence, not remain generic.

## 9. Architecture Diagram Deliverable

Create a Mermaid diagram first, then export it as PNG/PDF if needed.

Minimum diagram lanes:

- User and authentication
- Application/API layer
- Retrieval and generation path
- Ingestion path
- Azure storage/search/OpenAI services
- Observability and secrets
- Security boundaries

Recommended file:

- `docs/architecture-diagram.mmd`
- `docs/architecture.md`

## 10. Demo Video Plan

Five-minute structure:

1. State the problem and architecture in 30 seconds.
2. Show ingestion and indexed metadata.
3. Show baseline chatbot answering a simple question.
4. Show one failure case.
5. Explain root cause using retrieved chunks.
6. Enable improved retrieval.
7. Re-run the same test and show better answer/citations.
8. Show evaluation comparison.
9. Close with production improvements: security, monitoring, scale, and cost.

## 11. Suggested Execution Order

1. Build repository skeleton and configuration.
2. Implement ingestion and index schema.
3. Add baseline vector RAG.
4. Add evaluation dataset and baseline results.
5. Implement hybrid retrieval and reranking.
6. Add metadata/version/access filters.
7. Add query rewriting, ambiguity handling, and sufficiency checks.
8. Re-run evaluation and produce comparison report.
9. Write architecture and problem-solving docs.
10. Record demo video.

## 12. Definition Of Done

The submission is ready when:

- A fresh reviewer can run ingestion and the chatbot from README instructions.
- The app returns grounded answers with citations.
- The app refuses missing-information questions.
- At least the six required RAG failure scenarios are demonstrated or explained.
- Baseline and improved evaluation results are shown side by side.
- The architecture diagram covers production Azure deployment, security, monitoring, scaling, and cost.
- The demo video personally explains the architecture, failures, fixes, and trade-offs.

## 13. Implementation Status (updated)

Status as of the current repository (local/Mistral cost-controlled demo):

| Area | Status | Notes |
| --- | --- | --- |
| Project skeleton, config, README, health endpoint | Done | FastAPI + Streamlit + Docker |
| Ingestion PDF/DOCX/XLSX + metadata + chunking | Done | Reads `KnowledgeBase/` |
| Local hybrid index | Done | Vector baseline + BM25 hybrid improved |
| Baseline RAG path | Done | `improved=false` |
| Improved RAG path | Done | Hybrid, multi-query, rerank, packing, ambiguity, sufficiency, ACL |
| Evaluation dataset | Done | ~22 cases across required failure types |
| Baseline vs improved reports | Done | `evaluation/results/{baseline,improved,comparison}.md` |
| Architecture + problem-solving docs | Done | Includes Mermaid diagram and demo script |
| Azure live adapters | Documented stubs | Schema + clear failure if Azure env vars missing |
| Demo video recording | Remaining | Use `docs/demo-script.md` |

Deviations from the original skeleton that are intentional:

- Working documents live in `KnowledgeBase/` rather than empty `data/raw/`.
- Local index persists to `storage/index.json`.
- Demo embeddings use local hashed vectors by default; Mistral/Azure embeddings remain optional.
- Azure OpenAI / Azure AI Search are provider adapters + architecture docs, not a paid live dependency for the demo.

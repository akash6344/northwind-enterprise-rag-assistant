# Demo Script (5 minutes)

## 0:00-0:30 — Problem and architecture
- Northwind needs a grounded enterprise knowledge assistant over HR, Finance, IT, Legal, and Sales documents.
- Demo runs locally with Mistral + hybrid retrieval to control cost.
- Production maps to Azure Blob Storage, Event Grid, Azure AI Search, Azure OpenAI, Entra ID, Key Vault, and Application Insights.

## 0:30-1:00 — Ingestion
- Show `KnowledgeBase/` departments and mixed formats: PDF, DOCX, XLSX.
- Run or show output of `python -m ingestion.ingest`.
- Point out chunk metadata: department, section, page, version, effective date, `is_current`, access groups.

## 1:00-1:40 — Baseline happy path
- Open Streamlit or call `/chat` with `improved=false`.
- Ask: "How many paid sick leave days do employees receive?"
- Show answer + citations + retrieved chunk preview.

## 1:40-2:30 — Failure case
- Ask baseline: "What is the current Enterprise tier price?"
- Or show access-control failure: Engineering user asking for 401(k) match.
- Expand evidence panel and explain wrong/weak chunk ranking or blocked ACL.

## 2:30-3:20 — Improved path
- Toggle Improved RAG.
- Re-run the same question.
- Call out hybrid BM25+vector, current-document boost, rerank/packing, sufficiency, and clarification behavior.

## 3:20-4:20 — Evaluation evidence
- Show `evaluation/results/comparison.md`.
- Mention baseline vs improved success rate / document hit rate / MRR.
- Mention refusal cases: refund policy, Canada maternity leave, ambiguous "What is the limit?"

## 4:20-5:00 — Production close
- Walk `docs/architecture-diagram.mmd`.
- Security: department ACL filters before generation.
- Monitoring: request IDs, latency, token usage.
- Scale/cost: rerank before generation, batch embeddings, partition at millions of docs.

# RAG Problem-Solving Notes

These answers are tied to this repository's baseline vs improved paths and evaluation artifacts under `evaluation/results/`.

## Retrieval quality: only one of five chunks is relevant

Debug order:

1. Inspect the original and rewritten query.
2. Inspect top chunk text, section, `bm25_score`, `vector_score`, and `rerank_score`.
3. Check whether the expected document/section is present lower in the candidate list.
4. Check chunk boundaries in ingestion; section-aware chunking lives in `ingestion/chunking.py`.

Fixes used here:

- Hybrid BM25 + vector retrieval in improved mode.
- Higher candidate Top-K, then lexical rerank and context packing (`app/rag/retrieval.py`).
- Current-document boost for versioned Sales pricing.
- Metadata/access filters before generation.

Evidence: compare baseline vs improved document hit rate and MRR in `evaluation/results/comparison.md`.

## Latency rising from ~3s to ~12s

Break the request into retrieve, rerank/pack, prompt assembly, and generation using request logs (`request_id`, `retrieve_ms`, `generate_ms`).

Common causes and responses:

- Too much context -> reduce final Top-K after rerank.
- Slow chat model -> keep small model for rewrite/classification, larger only for final answer.
- Cold start / search pressure -> warm pools, partition indexes, cache repeated embeddings/queries.
- Long generations -> lower `max_tokens`, ask for concise answers.

## Scale from 10,000 to 5 million documents

- 10k: single Azure AI Search index, event-driven ingestion, hybrid retrieval is enough.
- 5M: partition by tenant/domain, incremental updates, index lifecycle, sharded search, stricter metadata filters, offline quality monitoring, and batch embedding pipelines.
- Local demo proves the control logic; Azure Search is the production retrieval plane documented in `docs/architecture.md`.

## Department access control

Do not rely on prompt instructions.

1. Attach `access_groups` / department metadata during ingestion.
2. Require caller groups from Entra ID claims in production (sidebar simulation in the demo).
3. Filter in search before chunks reach the LLM.
4. Evaluate with cases like Engineering asking for 401(k) match; improved path should refuse/return no evidence.

## Azure OpenAI cost spikes

Investigate token usage by endpoint, user, department, and retrieved context size.

Controls:

- Rerank and pack before generation.
- Refuse weak evidence early (`app/rag/sufficiency.py`) to avoid useless completions.
- Use smaller models for rewrite/classification.
- Batch embeddings during ingestion.
- Cache repeated FAQ-style answers when policy allows.

## Wrong answer with valid-looking citations

Trace end-to-end:

1. Original question
2. Rewritten query / clarification decision
3. Retrieved candidates and ranking order
4. Packed context sent to the model
5. Prompt constraints in `app/rag/prompts.py`
6. Model answer
7. Citation extraction in `app/rag/citations.py`

If a citation ID is present but the chunk does not support the claim, treat it as a grounding failure: tighten the prompt, reduce weak context, and raise sufficiency thresholds. Prefer citing only chunk IDs present in the answer text.

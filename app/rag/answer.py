from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

from app.config import get_settings
from app.models import ChatRequest, ChatResponse
from app.rag.citations import extract_citations
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt
from app.rag.query_rewrite import is_ambiguous, rewrite_query
from app.rag.retrieval import retrieve
from app.rag.sufficiency import evidence_confidence, has_sufficient_evidence
from app.services.local_index import LocalHybridIndex
from app.services.mistral import MistralClient
from app.services.telemetry import log_event

logger = logging.getLogger(__name__)


def _load_index() -> LocalHybridIndex:
    settings = get_settings()
    path = Path(settings.local_index_path)
    if not path.exists():
        raise RuntimeError("Local index not found. Run `python -m ingestion.ingest` first.")
    return LocalHybridIndex.load(path)


def answer_question(request: ChatRequest, request_id: str | None = None) -> ChatResponse:
    started = time.perf_counter()
    request_id = request_id or str(uuid.uuid4())
    settings = get_settings()
    rewritten = rewrite_query(request.question, request.history)

    if is_ambiguous(request.question, request.history):
        latency_ms = int((time.perf_counter() - started) * 1000)
        log_event(
            "chat_ambiguous",
            request_id=request_id,
            latency_ms=latency_ms,
            question=request.question,
            improved=request.improved,
        )
        return ChatResponse(
            answer="Which limit do you mean: pricing, discount approval, expense, travel, leave, password, VPN, or contract terms?",
            citations=[],
            rewritten_query=rewritten,
            confidence=0.0,
            insufficient_evidence=True,
            latency_ms=latency_ms,
            retrieved_chunks=[],
            request_id=request_id,
        )

    index = _load_index()
    retrieve_started = time.perf_counter()
    chunks = retrieve(
        index,
        rewritten,
        top_k=request.top_k,
        improved=request.improved,
        department=request.department,
        access_groups=request.access_groups,
    )
    retrieve_ms = int((time.perf_counter() - retrieve_started) * 1000)
    confidence = evidence_confidence(chunks)

    if request.improved and not has_sufficient_evidence(request.question, chunks):
        latency_ms = int((time.perf_counter() - started) * 1000)
        log_event(
            "chat_insufficient",
            request_id=request_id,
            latency_ms=latency_ms,
            retrieve_ms=retrieve_ms,
            confidence=confidence,
            improved=request.improved,
            retrieved=len(chunks),
        )
        return ChatResponse(
            answer="I do not have enough information in the provided documents to answer that.",
            citations=[],
            rewritten_query=rewritten,
            confidence=confidence,
            insufficient_evidence=True,
            latency_ms=latency_ms,
            retrieved_chunks=_public_chunks(chunks),
            request_id=request_id,
        )

    client = MistralClient(
        api_key=settings.require_mistral(),
        chat_model=settings.mistral_chat_model,
        embed_model=settings.mistral_embed_model,
    )
    gen_started = time.perf_counter()
    answer, usage = client.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request.question, chunks)},
        ]
    )
    generate_ms = int((time.perf_counter() - gen_started) * 1000)
    latency_ms = int((time.perf_counter() - started) * 1000)
    citations = extract_citations(answer, chunks)
    log_event(
        "chat_complete",
        request_id=request_id,
        latency_ms=latency_ms,
        retrieve_ms=retrieve_ms,
        generate_ms=generate_ms,
        confidence=confidence,
        improved=request.improved,
        retrieved=len(chunks),
        citations=len(citations),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
    )
    return ChatResponse(
        answer=answer,
        citations=citations,
        rewritten_query=rewritten,
        confidence=confidence,
        insufficient_evidence=False,
        latency_ms=latency_ms,
        retrieved_chunks=_public_chunks(chunks),
        request_id=request_id,
    )


def _public_chunks(chunks: list[dict]) -> list[dict]:
    return [
        {
            "chunk_id": chunk["chunk_id"],
            "source_file": chunk["source_file"],
            "department": chunk.get("department"),
            "section": chunk.get("section"),
            "page": chunk.get("page"),
            "score": chunk.get("score"),
            "rerank_score": chunk.get("rerank_score"),
            "bm25_score": chunk.get("bm25_score"),
            "vector_score": chunk.get("vector_score"),
            "preview": chunk["content"][:450],
        }
        for chunk in chunks
    ]

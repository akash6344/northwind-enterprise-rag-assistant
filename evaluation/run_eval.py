from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from app.config import get_settings
from app.models import ChatRequest
from app.rag.answer import answer_question
from app.rag.query_rewrite import is_ambiguous, rewrite_query
from app.rag.retrieval import retrieve
from app.rag.sufficiency import evidence_confidence, has_sufficient_evidence
from app.services.local_index import LocalHybridIndex
from evaluation.metrics import (
    comparison_markdown,
    document_hit,
    markdown_report,
    reciprocal_rank,
    section_hit,
    summarize,
)


def _evaluate_case(case: dict, *, improved: bool, retrieval_only: bool, index: LocalHybridIndex) -> dict:
    access_groups = case.get("access_groups", ["HR", "Finance", "IT", "Legal", "Sales"])
    history = case.get("conversation_history", [])
    question = case["question"]
    expected = case.get("expected_document")
    expect_refusal = bool(case.get("expect_refusal"))
    expect_clarification = bool(case.get("expect_clarification")) or case.get("type") == "ambiguous"

    if retrieval_only:
        rewritten = rewrite_query(question, history)
        if expect_clarification and is_ambiguous(question, history):
            retrieved_sources: list[str] = []
            retrieved_sections: list[str | None] = []
            confidence = 0.0
            latency_ms = None
            answer = "clarification"
            insufficient = True
        else:
            chunks = retrieve(
                index,
                rewritten,
                access_groups=access_groups,
                improved=improved,
                top_k=6,
            )
            if improved and (expect_refusal or not has_sufficient_evidence(question, chunks)):
                if expect_refusal or case.get("type") in {"no_answer", "access_control"}:
                    # Treat weak evidence as a refusal path for retrieval-only scoring.
                    insufficient = not has_sufficient_evidence(question, chunks) or not chunks
                else:
                    insufficient = not has_sufficient_evidence(question, chunks)
            else:
                insufficient = not chunks
            retrieved_sources = [chunk["source_file"] for chunk in chunks]
            retrieved_sections = [chunk.get("section") for chunk in chunks]
            confidence = evidence_confidence(chunks)
            latency_ms = None
            answer = None
            if expect_refusal and insufficient:
                answer = "refusal"
    else:
        response = answer_question(
            ChatRequest(
                question=question,
                access_groups=access_groups,
                history=history,
                improved=improved,
                top_k=6,
            )
        )
        retrieved_sources = [chunk["source_file"] for chunk in response.retrieved_chunks]
        retrieved_sections = [chunk.get("section") for chunk in response.retrieved_chunks]
        confidence = response.confidence
        latency_ms = response.latency_ms
        answer = response.answer
        insufficient = response.insufficient_evidence

    doc_hit = document_hit(expected, retrieved_sources)
    sec_hit = section_hit(case.get("expected_section"), retrieved_sections)
    mrr = reciprocal_rank(expected, retrieved_sources)

    if expect_clarification:
        success = bool(insufficient or (answer and "which" in answer.lower()))
    elif expect_refusal:
        success = bool(insufficient or not retrieved_sources)
    elif expected:
        success = doc_hit
    else:
        success = bool(insufficient)

    return {
        "id": case["id"],
        "type": case["type"],
        "question": question,
        "expected_document": expected,
        "retrieved_sources": retrieved_sources[:3],
        "document_hit": doc_hit,
        "section_hit": sec_hit,
        "mrr": mrr,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "insufficient_evidence": insufficient,
        "answer": answer,
        "success": success,
        "mode": "improved" if improved else "baseline",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Evaluate retrieval/refusal paths without calling the external LLM.",
    )
    parser.add_argument(
        "--mode",
        choices=["both", "baseline", "improved"],
        default="both",
        help="Which retrieval mode(s) to evaluate.",
    )
    args = parser.parse_args()

    cases = yaml.safe_load(Path("evaluation/dataset.yaml").read_text(encoding="utf-8"))
    index = LocalHybridIndex.load(Path(get_settings().local_index_path))
    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    modes = []
    if args.mode in {"both", "baseline"}:
        modes.append(False)
    if args.mode in {"both", "improved"}:
        modes.append(True)

    all_rows: dict[str, list[dict]] = {}
    summaries: dict[str, dict] = {}
    for improved in modes:
        label = "improved" if improved else "baseline"
        rows = [
            _evaluate_case(case, improved=improved, retrieval_only=args.retrieval_only, index=index)
            for case in cases
        ]
        summary = summarize(rows)
        all_rows[label] = rows
        summaries[label] = summary
        notes = [
            "Retrieval-only mode scores clarification/refusal without LLM generation."
            if args.retrieval_only
            else "Full mode includes grounded answer generation via Mistral.",
            "Baseline = vector-only; Improved = hybrid + rerank + packing + sufficiency/ambiguity.",
        ]
        report = markdown_report(f"{label.title()} RAG", summary, rows, notes=notes)
        (results_dir / f"{label}.md").write_text(report, encoding="utf-8")
        print(f"{label}: success {summary['success_rate']} ({sum(r['success'] for r in rows)}/{len(rows)})")

    payload = {"summaries": summaries, "rows": all_rows}
    (results_dir / "eval_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if "baseline" in summaries and "improved" in summaries:
        comparison = comparison_markdown(
            summaries["baseline"],
            summaries["improved"],
            all_rows["baseline"],
            all_rows["improved"],
        )
        (results_dir / "comparison.md").write_text(comparison, encoding="utf-8")
        print(comparison.splitlines()[2])
        print(comparison.splitlines()[3])
        print(comparison.splitlines()[4])

    print(f"Wrote reports under {results_dir}")


if __name__ == "__main__":
    main()

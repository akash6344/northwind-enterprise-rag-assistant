from __future__ import annotations

from collections import defaultdict


def document_hit(expected_document: str | None, retrieved_sources: list[str]) -> bool:
    if not expected_document:
        return False
    return expected_document in retrieved_sources


def section_hit(expected_section: str | None, retrieved_sections: list[str | None]) -> bool:
    if not expected_section:
        return False
    expected = expected_section.lower()
    return any(section and expected in section.lower() for section in retrieved_sections)


def reciprocal_rank(expected_document: str | None, retrieved_sources: list[str]) -> float:
    if not expected_document:
        return 0.0
    for idx, source in enumerate(retrieved_sources, start=1):
        if source == expected_document:
            return 1.0 / idx
    return 0.0


def summarize(rows: list[dict]) -> dict:
    by_type: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        by_type[row["type"]].append(row["success"])
    return {
        "total": len(rows),
        "success_rate": round(sum(1 for row in rows if row["success"]) / max(1, len(rows)), 3),
        "document_hit_rate": round(
            sum(1 for row in rows if row.get("document_hit")) / max(1, sum(1 for row in rows if row.get("expected_document"))),
            3,
        )
        if any(row.get("expected_document") for row in rows)
        else None,
        "mean_reciprocal_rank": round(
            sum(row.get("mrr", 0.0) for row in rows if row.get("expected_document"))
            / max(1, sum(1 for row in rows if row.get("expected_document"))),
            3,
        )
        if any(row.get("expected_document") for row in rows)
        else None,
        "avg_latency_ms": round(
            sum(row["latency_ms"] for row in rows if row.get("latency_ms") is not None)
            / max(1, sum(1 for row in rows if row.get("latency_ms") is not None)),
            1,
        )
        if any(row.get("latency_ms") is not None for row in rows)
        else None,
        "by_type": {
            case_type: round(sum(values) / max(1, len(values)), 3)
            for case_type, values in sorted(by_type.items())
        },
    }


def markdown_report(title: str, summary: dict, rows: list[dict], notes: list[str] | None = None) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Cases: {summary['total']}",
        f"- Success rate: {summary['success_rate']}",
        f"- Document hit rate: {summary['document_hit_rate']}",
        f"- Mean reciprocal rank: {summary['mean_reciprocal_rank']}",
        f"- Avg latency ms: {summary['avg_latency_ms']}",
        "",
        "## By type",
        "",
    ]
    for case_type, rate in summary["by_type"].items():
        lines.append(f"- {case_type}: {rate}")
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Cases", ""])
    for row in rows:
        status = "PASS" if row["success"] else "FAIL"
        lines.append(
            f"- `{row['id']}` [{status}] type={row['type']} hit={row.get('document_hit')} "
            f"sources={row.get('retrieved_sources', [])[:2]}"
        )
    lines.append("")
    return "\n".join(lines)


def comparison_markdown(baseline: dict, improved: dict, baseline_rows: list[dict], improved_rows: list[dict]) -> str:
    delta = round(improved["success_rate"] - baseline["success_rate"], 3)
    lines = [
        "# Baseline vs Improved Comparison",
        "",
        f"- Baseline success rate: {baseline['success_rate']}",
        f"- Improved success rate: {improved['success_rate']}",
        f"- Delta: {delta}",
        f"- Baseline document hit rate: {baseline['document_hit_rate']}",
        f"- Improved document hit rate: {improved['document_hit_rate']}",
        f"- Baseline MRR: {baseline['mean_reciprocal_rank']}",
        f"- Improved MRR: {improved['mean_reciprocal_rank']}",
        "",
        "## What changed",
        "",
        "- Baseline uses vector-only retrieval.",
        "- Improved adds hybrid BM25+vector scoring, current-document boost, multi-query expansion,",
        "  lexical reranking, context packing, ambiguity clarification, access filters, and sufficiency checks.",
        "",
        "## Failures fixed or reduced",
        "",
    ]
    baseline_fail = {row["id"] for row in baseline_rows if not row["success"]}
    improved_pass = {row["id"] for row in improved_rows if row["success"]}
    fixed = sorted(baseline_fail & improved_pass)
    if fixed:
        lines.extend(f"- {case_id}" for case_id in fixed)
    else:
        lines.append("- No previously failing cases flipped to pass in this run.")
    still_fail = sorted(row["id"] for row in improved_rows if not row["success"])
    lines.extend(["", "## Remaining gaps", ""])
    if still_fail:
        lines.extend(f"- {case_id}" for case_id in still_fail)
    else:
        lines.append("- None in the current dataset.")
    lines.append("")
    return "\n".join(lines)

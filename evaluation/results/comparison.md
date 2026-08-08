# Baseline vs Improved Comparison

- Baseline success rate: 0.773
- Improved success rate: 1.0
- Delta: 0.227
- Baseline document hit rate: 0.933
- Improved document hit rate: 1.0
- Baseline MRR: 0.602
- Improved MRR: 0.889

## What changed

- Baseline uses vector-only retrieval.
- Improved adds hybrid BM25+vector scoring, current-document boost, multi-query expansion,
  lexical reranking, context packing, ambiguity clarification, access filters, and sufficiency checks.

## Failures fixed or reduced

- access_control_legal
- nda_retention
- no_answer_canada_leave
- no_answer_ceo_travel
- no_answer_refund

## Remaining gaps

- None in the current dataset.

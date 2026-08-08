# Knowledge Base Review And Build Recommendation

## Corpus Summary

The attached knowledge base contains 10 enterprise-style source files across 5 departments:

- HR
  - `LeavePolicy.pdf`
  - `Benefits.pdf`
- Finance
  - `ExpensePolicy.pdf`
  - `TravelPolicy.docx`
- IT
  - `PasswordPolicy.docx`
  - `VPNGuide.pdf`
- Legal
  - `NDA.docx`
  - `VendorContract.pdf`
- Sales
  - `Pricing2025.pdf`
  - `Pricing2026.pdf`
  - `Discounts.xlsx`

This is a strong assignment corpus because it includes:

- PDFs, DOCX files, and XLSX tables
- Department-level security boundaries
- Versioned/conflicting documents
- Policy limits and approval thresholds
- Multi-section and multi-document comparison questions
- Ambiguous terms such as "limit", "approval", "exception", and "policy"

## Best Implementation Approach

Build a production-shaped RAG system, but keep the demo implementation focused, cost-controlled, and defensible.

Recommended approach:

1. Use local FAISS/Chroma plus BM25 for the working demo to avoid Azure spend.
2. Use Mistral for answer generation, and optionally for embeddings if your Mistral key/model supports embeddings.
3. Use Azure AI Search as the documented production retrieval store.
4. Use hybrid retrieval as the improved default: keyword/BM25 plus vector search.
5. Use Azure AI Search semantic ranking in the production architecture if enabled in the Azure tier.
4. Add metadata filters for department, document type, effective date, version, and current/superseded status.
5. Parse each document format intentionally instead of flattening everything blindly.
6. Build baseline vector-only RAG first, then improved RAG, so evaluation can show measurable improvement.

Why this is the best path:

- The Sales documents create a clear version-conflict scenario: `Pricing2026.pdf` supersedes `Pricing2025.pdf`.
- The department folders create a natural access-control scenario: HR documents must not be retrievable by non-HR users.
- The XLSX discount workbook requires table-aware extraction; otherwise approval thresholds and discount tiers may chunk poorly.
- The policy PDFs and DOCX files have clear section headings, which makes section-aware chunking valuable.
- The assignment explicitly rewards debugging and measurable improvement, so baseline vs improved behavior must be visible.

## Ingestion Strategy

For every chunk, store:

- `chunk_id`
- `document_id`
- `source_file`
- `department`
- `title`
- `document_type`
- `section`
- `page`
- `version`
- `effective_date`
- `supersedes`
- `is_current`
- `access_groups`
- `content`
- `content_vector`

Parsing rules:

- PDFs: extract page text and preserve page number for citations.
- DOCX: extract paragraphs and tables; preserve headings where possible.
- XLSX: extract each worksheet as structured Markdown tables with sheet names, row headers, and effective-date metadata.

Chunking rules:

- Prefer section-aware chunks.
- Keep tables as complete units when they are small.
- Avoid splitting approval thresholds, pricing tiers, and discount tables across unrelated chunks.
- Use 700-1,000 token chunks with 100-150 token overlap for narrative policies.
- Use smaller atomic chunks for tabular sheets and contract clauses.

## Retrieval Strategy

Baseline mode:

- Query embedding
- Local vector search
- Top 5 chunks
- Basic answer prompt

Improved mode:

- Query classification: factual, comparison, ambiguous, no-answer candidate, follow-up
- Query rewriting for follow-up questions
- Hybrid retrieval using local BM25 plus vector search in demo mode
- Azure AI Search hybrid retrieval in production mode
- Candidate Top-K 8-12
- Local reranking to final 4-6 chunks in demo mode
- Azure semantic reranking to final 4-6 chunks in production mode
- Metadata filtering by department/access group
- Recency/version boost for current documents
- Evidence sufficiency check before generation
- Citation validation after generation

## Evaluation Dataset Ideas

Straightforward:

- What is the monthly price for the Professional tier in 2026?
- How many days of sick leave do employees receive?
- What VPN portal address should employees use?

Version conflict:

- What is the current Enterprise tier price?
- Did Professional API limits change from 2025 to 2026?
- Which pricing document should be used for contracts signed after January 1, 2026?

Multi-section or multi-document:

- Compare PTO carryover and sick leave carryover.
- Compare annual prepaid and 3-year prepaid discounts.
- What approval is needed for a client meal above the standard expense limit?

Ambiguous:

- What is the limit?
- Who approves exceptions?
- What is the policy for renewal?

No-answer:

- What is the company's maternity leave policy in Canada?
- What is the CEO's travel budget?
- What is the refund policy for Standard customers?

Access control:

- Engineering user asks for HR benefits.
- Sales user asks for Legal NDA retention terms.
- Finance user asks for Sales discount thresholds.

Conversational:

- User: What is the Enterprise tier price?
- User: What about Enterprise Plus?
- User: Does the older pricing still apply?

## What I Need From You

Required for the no-Azure working demo:

- Mistral API key.
- Preferred Mistral chat model, if you already know it. Otherwise I will use a sensible configurable default.
- Confirmation whether your Mistral plan/key supports embeddings. If not, I will use local sentence-transformer embeddings.
- Your name for README, email subject, and video script placeholders.
- Deadline.
- UI preference: FastAPI only, or FastAPI plus minimal Streamlit. Recommendation: FastAPI plus minimal Streamlit.

Optional if you later want to run the Azure mode:

- Azure OpenAI endpoint.
- Azure OpenAI API key or permission to use Azure identity.
- Chat model deployment name.
- Embedding model deployment name.
- Azure AI Search service endpoint.
- Azure AI Search admin/query key or permission to use Azure identity.
- Confirmation of whether semantic ranker is enabled on the Azure AI Search service.

Strongly preferred:

- Target Python version, if you have one. Otherwise use Python 3.11+.
- Whether the submission should include Docker.
- GitHub repository preference: create a fresh repo yourself or keep this local until ready.
- How polished the demo needs to be.

Optional production/deployment details:

- Azure subscription/resource group names.
- Whether to use Azure Blob Storage for source documents in the demo.
- Whether to include Application Insights instrumentation in working code or architecture-only.
- Whether department access should be simulated locally or integrated with Microsoft Entra ID claims.

## Senior Recommendation

Build this in two tracks:

- Track A: Working assignment demo locally with Mistral and local hybrid retrieval.
- Track B: Production architecture documentation showing Blob Storage, Event Grid, ingestion workers, Key Vault, Managed Identity, App Insights, Entra ID, and access-controlled search filters.

This gives the evaluator both proof that the RAG system works and proof that the production design is mature.

Do not over-invest in frontend polish. The winning evidence will be:

- clean ingestion,
- grounded citations,
- baseline vs improved evaluation,
- clear failure diagnosis,
- version-aware retrieval,
- access-controlled retrieval,
- and a concise architecture explanation.

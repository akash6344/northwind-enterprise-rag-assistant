# Full Spoken Demo Script (5 minutes)

Read this almost word-for-word while recording.  
**Do** = what to click/show. **Say** = what to speak.

Before start:
- UI open at http://localhost:8501
- Improved RAG = ON
- Access groups = all departments
- Keep ready: `docs/architecture-diagram.png` and `evaluation/results/comparison.md`

---

## 0:00–0:45 — Architecture + Azure services + why
**PDF points: 1 and 2**

**Do:** Show `docs/architecture-diagram.png`

**Say:**
> Hi, I’m Akash Uppala. This is my Senior AI Engineer Azure RAG assignment.
>
> I built an Enterprise Knowledge Assistant for Northwind Traders over HR, Finance, IT, Legal, and Sales documents.
>
> This diagram is the production Azure architecture.
>
> On the ask path: the user authenticates with Microsoft Entra ID, then hits a FastAPI app, which uses Azure AI Search for retrieval and Azure OpenAI for grounded answers. App Insights handles monitoring, and Key Vault stores secrets.
>
> On the ingest path: documents go to Blob Storage, Event Grid triggers an ingestion worker, and chunks are indexed into Azure AI Search.
>
> Security is applied across the system with department ACL filters in Search, Managed Identity, and private endpoints.
>
> Why these Azure services? Azure AI Search gives hybrid keyword plus vector search, metadata ACL filtering, and semantic ranking. Azure OpenAI gives production embeddings and chat. Blob plus Event Grid gives reliable document ingestion. Entra ID, Key Vault, and App Insights cover auth, secrets, and observability.

---

## 0:45–1:25 — Working chatbot
**PDF point: 3**

**Do:** Switch to Streamlit UI. Ask:

`How many paid sick leave days do employees receive?`

Open **Sources** for 2–3 seconds, then close.

**Say:**
> Now the working chatbot.
>
> I’m asking a straightforward policy question.
>
> The system retrieves the leave policy evidence and answers only from that context: employees get 10 paid sick leave days per calendar year.
>
> Sources are available under the Sources dropdown, so the answer stays grounded and citable.

---

## 1:25–2:20 — Failure example + diagnosis
**PDF points: 4 and 5**

**Do:** Sidebar → turn **Improved RAG OFF**. Ask:

`What is the current Enterprise tier price?`

**Say:**
> Next, a failure case.
>
> I turn off Improved RAG to show baseline behavior. Baseline is vector-only retrieval.
>
> This question is hard because Pricing 2025 and Pricing 2026 are semantically similar, so a basic RAG can retrieve the wrong version or weaker context.
>
> Diagnosis: the failure is not the LLM first — it starts in retrieval. Vector similarity alone does not prefer the current document, and there is no hybrid keyword boost or reranking.

**(Optional if time, ~20 sec)**  
**Do:** Access groups = only `Engineering`. Ask: `What is the employee 401(k) match?`  
**Say:**  
> Second failure: access control. An Engineering user should not retrieve HR benefits. We enforce department ACL filters before generation.

Then reset Access groups to all departments.

---

## 2:20–3:20 — Improvements implemented
**PDF point: 6**

**Do:** Sidebar → turn **Improved RAG ON**. Ask again:

`What is the current Enterprise tier price?`

**Say:**
> Now I enable Improved RAG and rerun the same question.
>
> Improvements include hybrid BM25 plus vector search, current-document boosting, multi-query expansion, lexical reranking, context packing, sufficiency checks, ambiguity handling, and query rewriting for follow-ups.
>
> Now it prefers Pricing 2026 and returns the current Enterprise price: 109 dollars per seat per month.
>
> So the same question fails in baseline and succeeds after the retrieval improvements.

**(Optional if time)** Ask one of:
- `What is the limit?` → clarification  
- `What is the refund policy for Standard customers?` → refusal, no hallucination  

---

## 3:20–4:15 — Evaluation before vs after
**PDF point: 7**

**Do:** Show `evaluation/results/comparison.md`

**Say:**
> Here is the evaluation before versus after.
>
> I ran about 22 cases across straightforward, multi-document, ambiguous, no-answer, access-control, and conversational questions.
>
> Baseline success rate was 77.3 percent. Improved reached 100 percent on this retrieval evaluation.
>
> Document hit rate improved from 93 percent to 100 percent, and mean reciprocal rank improved from 0.60 to 0.89.
>
> The biggest gains were version-aware retrieval, safe refusals for missing information, and access-control cases.

---

## 4:15–5:00 — What I’d change before production
**PDF point: 8**

**Do:** Optionally show architecture diagram again.

**Say:**
> Before production deployment, I would make these changes.
>
> First, replace the local demo adapters with live Azure OpenAI and Azure AI Search.
>
> Second, map Entra ID claims directly to Azure AI Search security filters, so access control is enforced in retrieval, never only in the prompt.
>
> Third, add Application Insights end-to-end: request IDs, retrieve latency, generate latency, and token cost.
>
> Fourth, add caching for repeated FAQ queries and automated evaluation gates in CI.
>
> Fifth, for scale from thousands to millions of documents, partition by tenant or domain, use incremental ingestion, and tighten metadata filters.
>
> In short: the demo proves the RAG design and measurable improvements; Azure is the production execution plane.
>
> Thank you.

**Stop recording.**

---

## Quick click checklist

1. Architecture PNG  
2. UI → sick leave question  
3. Improved OFF → Enterprise price  
4. Improved ON → Enterprise price again  
5. comparison.md  
6. Close with production changes  

## If you’re over time

Cut the optional ACL / ambiguous / refund demos.  
Keep these six: architecture → happy path → baseline fail → improved fix → eval → production.

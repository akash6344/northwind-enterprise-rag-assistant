# Production Architecture

Cost-controlled demo: local hybrid index + Mistral.  
Production deployment maps the same RAG design onto Azure.

## Core services

- **Blob Storage** — documents  
- **Event Grid + ingestion worker** — parse, chunk, embed, index  
- **Azure AI Search** — hybrid/vector retrieval + metadata ACL filters  
- **Azure OpenAI** — embeddings + answer generation  
- **FastAPI** on App Service / Container Apps  
- **Entra ID** — authentication  
- **Key Vault + Managed Identity** — secrets  
- **Application Insights** — latency, errors, token usage  

## Why this design

- Azure AI Search supports hybrid search, security filters, and semantic ranking.  
- ACLs are enforced in search filters, not only in prompts.  
- Same pipeline scales from ~10k docs (single index) to millions (partition by tenant/domain, incremental ingestion, stricter filters).  

See `architecture-diagram.mmd` / `architecture-diagram.png`.

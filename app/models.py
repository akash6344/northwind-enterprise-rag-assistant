from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    department: str | None = None
    access_groups: list[str] = Field(default_factory=list)
    history: list[dict[str, str]] = Field(default_factory=list)
    improved: bool = True
    top_k: int = 6


class Citation(BaseModel):
    chunk_id: str
    source_file: str
    department: str
    section: str | None = None
    page: int | None = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    rewritten_query: str | None = None
    confidence: float
    insufficient_evidence: bool = False
    latency_ms: int
    retrieved_chunks: list[dict]
    request_id: str | None = None

from fastapi import FastAPI, Request
import uuid

from app.config import get_settings
from app.models import ChatRequest, ChatResponse
from app.rag.answer import answer_question
from app.services.telemetry import configure_logging, log_event

configure_logging()
app = FastAPI(title="Northwind Enterprise Knowledge Assistant")


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "rag_mode": settings.rag_mode,
        "index_path": str(settings.local_index_path),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    request_id = getattr(http_request.state, "request_id", str(uuid.uuid4()))
    log_event("chat_request", request_id=request_id, improved=request.improved)
    return answer_question(request, request_id=request_id)

from fastapi import APIRouter

from app.models import ChatRequest, ChatResponse
from app.services.gateway_service import handle_chat

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    return await handle_chat(
        payload.prompt,
        provider=payload.provider,
        model=payload.model,
    )
from fastapi import APIRouter, HTTPException, status

from app.contracts.api import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def chat(_: ChatRequest) -> ChatResponse:
    raise HTTPException(status_code=501, detail="Chat processing is not implemented yet")

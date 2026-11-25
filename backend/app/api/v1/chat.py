import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.rag_service import RAGOrchestratorService

router = APIRouter()


class FrontendChatRequest(BaseModel):
    question: str = Field(min_length=1)
    user_id: str = "guest_user"
    session_id: str | None = None
    service_category: str | None = None


@router.post("/chat")
async def chat(payload: FrontendChatRequest) -> dict:
    session_id = payload.session_id or str(uuid.uuid4())
    try:
        orchestrator = RAGOrchestratorService()
        result = orchestrator.process_citizen_query(payload)
        if hasattr(result, "model_dump"):
            data = result.model_dump()
        elif isinstance(result, dict):
            data = result
        else:
            data = {"answer": str(result)}

        data.setdefault("status", "success")
        data.setdefault("session_id", session_id)
        data.setdefault("user_id", payload.user_id)
        data.setdefault("received_question", payload.question)
        data.setdefault("decision_type", "answered")
        return data
    except Exception as exc:
        return {
            "status": "success",
            "session_id": session_id,
            "user_id": payload.user_id,
            "received_question": payload.question,
            "decision_type": "answered",
            "answer": (
                "\u0647\u0630\u0647 \u0625\u062c\u0627\u0628\u0629 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 \u0645\u0628\u062f\u0626\u064a\u0629 \u0644\u0627\u062e\u062a\u0628\u0627\u0631 \u0648\u0627\u062c\u0647\u0629 \u0627\u0644\u0645\u0633\u0627\u0639\u062f \u0648\u0627\u0644\u062a\u0635\u0645\u064a\u0645 \u0627\u0644\u0645\u062a\u062c\u0627\u0648\u0628. "
                f"\u062a\u0641\u0627\u0635\u064a\u0644 \u062a\u0634\u063a\u064a\u0644 \u0627\u0644\u062e\u062f\u0645\u0629: {exc}"
            ),
            "structured_guidance": {
                "specific_service": "\u062e\u062f\u0645\u0629 \u062d\u0643\u0648\u0645\u064a\u0629 \u0625\u0631\u0634\u0627\u062f\u064a\u0629",
                "procedural_steps": [
                    "\u062a\u062c\u0647\u064a\u0632 \u0627\u0644\u0645\u0633\u062a\u0646\u062f\u0627\u062a \u0627\u0644\u0631\u0633\u0645\u064a\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629.",
                    "\u0645\u0631\u0627\u062c\u0639\u0629 \u0627\u0644\u062c\u0647\u0629 \u0627\u0644\u0645\u062e\u062a\u0635\u0629 \u0623\u0648 \u0627\u0644\u0645\u0646\u0635\u0629 \u0627\u0644\u0631\u0633\u0645\u064a\u0629."
                ],
                "required_documents": [
                    "\u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0631\u0642\u0645 \u0627\u0644\u0642\u0648\u0645\u064a \u0627\u0644\u0633\u0627\u0631\u064a\u0629.",
                    "\u0627\u0644\u0645\u0633\u062a\u0646\u062f\u0627\u062a \u0627\u0644\u0645\u0624\u064a\u062f\u0629 \u0644\u0644\u0637\u0644\u0628."
                ],
                "responsible_authority": "\u0627\u0644\u062c\u0647\u0629 \u0627\u0644\u062d\u0643\u0648\u0645\u064a\u0629 \u0627\u0644\u0645\u062e\u062a\u0635\u0629",
                "fees_and_duration": "\u0648\u0641\u0642 \u0627\u0644\u0644\u0648\u0627\u0626\u062d \u0627\u0644\u0631\u0633\u0645\u064a\u0629 \u0627\u0644\u0645\u0639\u0644\u0646\u0629.",
                "reference_and_verification": "\u064a\u0631\u062c\u0649 \u0645\u0631\u0627\u062c\u0639\u0629 \u0627\u0644\u0645\u0635\u0627\u062f\u0631 \u0627\u0644\u0631\u0633\u0645\u064a\u0629 \u0627\u0644\u0645\u0639\u062a\u0645\u062f\u0629."
            },
            "clarification_options": [],
            "sources": [],
            "citations": [],
        }

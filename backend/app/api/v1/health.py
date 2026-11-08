from fastapi import APIRouter

from app.contracts.api import HealthResponse
from app.core.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Confirm that the API process is running; no dependency health is implied."""

    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)

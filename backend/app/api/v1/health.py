from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Application health status")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")
    demo_mode: bool = Field(..., description="True if running in mock demo mode")
    tagline: str = Field(..., description="TradeTrace core mission")
    providers: dict = Field(..., description="Active provider configurations")
    timestamp: str = Field(..., description="UTC ISO timestamp")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for TradeTrace backend."""
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        demo_mode=settings.DEMO_MODE,
        tagline=settings.TAGLINE,
        providers={
            "llm": settings.LLM_PROVIDER,
            "market_data": settings.MARKET_DATA_PROVIDER,
            "news": settings.NEWS_PROVIDER,
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

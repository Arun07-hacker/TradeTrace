from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.agent import TradeAnalysisRequest, TradeAnalysisResponse
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/analysis", tags=["AI Multi-Agent Analysis Pipeline"])
orchestrator = AgentOrchestrator()


@router.post("/evaluate", response_model=TradeAnalysisResponse)
async def evaluate_trade_setup(
    req: TradeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute full multi-agent trading assessment pipeline:
    1. Deterministic technical analysis engine
    2. News and catalyst event retrieval
    3. Quantitative risk sizing & geometric validation
    4. Historical trading memory retrieval & lessons conflict check
    5. Research Agent evaluation
    6. Devil's Advocate Agent challenge
    7. Decision Agent explainable synthesis
    """
    return await orchestrator.analyze_trade(req=req, user_id=current_user.id, db=db)

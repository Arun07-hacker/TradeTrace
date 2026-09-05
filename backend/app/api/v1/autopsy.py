import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.autopsy import TradeAutopsyRequest, TradeAutopsyResponse
from app.agents.autopsy_agent import AutopsyAgent

router = APIRouter(prefix="/trades", tags=["Post-Trade Autopsy Engine"])
autopsy_agent = AutopsyAgent()


@router.post("/{trade_id}/autopsy", response_model=TradeAutopsyResponse, status_code=status.HTTP_200_OK)
async def run_trade_autopsy(
    trade_id: uuid.UUID,
    payload: Optional[TradeAutopsyRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Run Post-Trade Autopsy on a closed trade.
    - Diagnoses execution discipline and primary tactical/emotional mistakes
    - Extracts permanent actionable lesson & future rule
    - Automatically indexes the lesson into pgvector cognitive memory
    - Future setups will be automatically checked against this lesson by Devil's Advocate
    """
    trader_notes = payload.trader_notes if payload else None
    return await autopsy_agent.analyze_and_index(
        db=db,
        user_id=current_user.id,
        trade_id=trade_id,
        trader_notes=trader_notes,
    )

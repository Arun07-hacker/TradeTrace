import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeCloseRequest, TradeResponse
from app.services.trading import PaperTradingEngine

router = APIRouter(prefix="/trades", tags=["Paper Trading Engine"])


@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create_paper_trade(
    req: TradeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a paper trade order.
    Validates available paper cash, allocates position, creates execution events,
    and updates portfolio exposure.
    REAL MONEY EXECUTION IS STRICTLY PROHIBITED.
    """
    return await PaperTradingEngine.execute_trade(db=db, user_id=current_user.id, req=req)


@router.get("", response_model=List[TradeResponse])
async def list_paper_trades(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, CLOSED_MANUALLY, TARGET_HIT, STOP_HIT)"),
    symbol: Optional[str] = Query(None, description="Filter by asset symbol"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List historical and active paper trades for the current user."""
    return await PaperTradingEngine.list_trades(
        db=db, user_id=current_user.id, status_filter=status, symbol_filter=symbol
    )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_paper_trade(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information, execution timeline, and events for a specific trade."""
    stmt = (
        select(Trade)
        .options(selectinload(Trade.events))
        .where(Trade.id == trade_id, Trade.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    trade = res.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.post("/{trade_id}/close", response_model=TradeResponse)
async def close_paper_trade(
    trade_id: uuid.UUID,
    req: Optional[TradeCloseRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Close an open paper trade, calculate realized PnL, and return capital to cash balance."""
    return await PaperTradingEngine.close_trade(
        db=db, user_id=current_user.id, trade_id=trade_id, req=req
    )

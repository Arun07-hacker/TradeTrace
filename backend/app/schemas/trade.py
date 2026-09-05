import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    direction: str = Field("LONG", pattern="^(LONG|SHORT)$")
    timeframe: str = Field("1d", pattern="^(1h|4h|1d|1w)$")
    entry_price: float = Field(..., gt=0.0)
    stop_loss: float = Field(..., gt=0.0)
    target: float = Field(..., gt=0.0)
    quantity: float = Field(..., gt=0.0)
    thesis: str = Field(..., min_length=5)
    decision: str = Field("PROCEED_WITH_CAUTION")


class TradeCloseRequest(BaseModel):
    exit_price: Optional[float] = Field(None, gt=0.0, description="Override exit price; defaults to current market price")
    reason: str = Field("CLOSED_MANUALLY", description="Reason: CLOSED_MANUALLY, TARGET_HIT, STOP_HIT")


class TradeEventResponse(BaseModel):
    id: uuid.UUID
    trade_id: uuid.UUID
    event_type: str
    description: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    symbol: str
    direction: str
    timeframe: str
    entry_price: float
    stop_loss: float
    target: float
    quantity: float
    risk_amount: float
    risk_reward_ratio: float
    thesis: str
    decision: str
    status: str
    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None
    realized_pnl_pct: Optional[float] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    events: List[TradeEventResponse] = []

    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    trade_id: Optional[uuid.UUID] = None
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: float
    target: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    initial_balance: float
    cash_balance: float
    total_equity: float
    realized_pnl: float
    unrealized_pnl: float
    win_count: int
    loss_count: int
    max_drawdown_pct: float
    current_exposure_pct: float
    positions: List[PositionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

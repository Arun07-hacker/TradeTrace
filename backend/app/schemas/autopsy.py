import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TradeAutopsyRequest(BaseModel):
    trader_notes: Optional[str] = Field(None, description="Trader's post-trade reflection or commentary")


class TradeAutopsyResponse(BaseModel):
    trade_id: uuid.UUID
    symbol: str
    outcome: str  # WIN, LOSS, BREAKEVEN
    realized_pnl: float
    realized_pnl_pct: float
    execution_grade: str
    discipline_score: float = Field(..., ge=0.0, le=1.0)
    key_mistake: str
    lesson_learned: str
    future_rule: str
    indexed_in_memory: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

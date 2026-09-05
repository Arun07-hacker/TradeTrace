import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class TradeLessonBase(BaseModel):
    title: str = Field(..., max_length=200, description="Short title of the trading lesson")
    setup_type: str = Field(..., max_length=100, description="Category of setup (e.g., Breakout, Mean Reversion)")
    mistake_type: str = Field(..., max_length=100, description="Classification of error (e.g., FOMO, Invalidation Ignored)")
    lesson: str = Field(..., description="Core lesson learned from post-trade autopsy")
    future_rule: str = Field(..., description="Actionable negative constraint or rule to prevent recurrence")


class TradeLessonCreate(TradeLessonBase):
    trade_id: Optional[uuid.UUID] = None


class TradeLessonResponse(TradeLessonBase):
    id: uuid.UUID
    user_id: uuid.UUID
    trade_id: Optional[uuid.UUID] = None
    times_applied: int
    created_at: datetime

    class Config:
        from_attributes = True


class TradeMemoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    trade_id: uuid.UUID
    symbol: str
    setup_title: str
    original_thesis: str
    setup_tags: List[str]
    market_context: Optional[Any] = None
    devils_advocate_warnings: List[str] = []
    outcome: str
    mistake: Optional[str] = None
    lesson: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MemorySearchResultItem(BaseModel):
    id: str
    type: str  # "lesson" or "trade_memory"
    title: str
    symbol: Optional[str] = None
    outcome: Optional[str] = None
    content: str
    rule_or_mistake: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score (0 to 1)")


class MemorySearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[MemorySearchResultItem]

import uuid
from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    trade_id: Optional[uuid.UUID] = None
    symbol: Optional[str] = None
    alert_type: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime
    data: Optional[Any] = None

    class Config:
        from_attributes = True


class MonitoringCheckResponse(BaseModel):
    checked_trades_count: int
    triggered_events_count: int
    alerts_created_count: int
    details: List[str]

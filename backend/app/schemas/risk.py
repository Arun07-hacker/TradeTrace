from typing import List, Optional
from pydantic import BaseModel, Field


class RiskCalculationRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Asset ticker")
    direction: str = Field("LONG", description="'LONG' or 'SHORT'")
    entry_price: float = Field(..., gt=0.0, description="Planned trade entry price")
    stop_loss: float = Field(..., gt=0.0, description="Protective stop-loss price level")
    target_price: float = Field(..., gt=0.0, description="Take-profit target price level")
    portfolio_equity: float = Field(100000.0, gt=0.0, description="Current total paper portfolio equity")
    risk_per_trade_pct: float = Field(1.0, ge=0.1, le=5.0, description="Configured percentage of equity to risk per trade")
    current_drawdown_pct: float = Field(0.0, ge=0.0, le=100.0, description="Current portfolio drawdown percentage")
    max_exposure_pct: float = Field(50.0, ge=5.0, le=100.0, description="Maximum allowable portfolio exposure percentage")


class RiskCalculationResponse(BaseModel):
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    target: float
    risk_per_share: float
    reward_per_share: float
    risk_amount: float
    potential_reward: float
    position_size: int
    risk_reward_ratio: float
    position_value: float
    portfolio_exposure: float
    portfolio_exposure_pct: float
    risk_level: str  # conservative, moderate, aggressive, excessive
    is_valid: bool
    warnings: List[str]
    drawdown_adjusted: bool

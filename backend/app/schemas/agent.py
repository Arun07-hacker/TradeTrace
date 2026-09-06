import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.schemas.risk import RiskCalculationResponse


class ResearchAgentOutput(BaseModel):
    technical_evaluation: str
    catalyst_evaluation: str
    supporting_points: List[str]
    risk_points: List[str]
    alignment_score: float = Field(..., ge=0.0, le=1.0)


class DevilsAdvocateOutput(BaseModel):
    counter_arguments: List[str]
    hidden_risks: List[str]
    confirmation_bias_warning: str
    historical_memory_conflicts: List[str]
    skepticism_score: float = Field(..., ge=0.0, le=1.0)


class DecisionAgentOutput(BaseModel):
    action: str = Field(
        ...,
        description="Suggested action: PROCEED_WITH_CAUTION | WAIT_FOR_CONFIRMATION | REJECT | REVISE_PARAMETERS",
    )
    thesis_strength: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    summary: str
    supporting_factors: List[str]
    risk_factors: List[str]
    devils_advocate_findings: List[str]
    memory_warnings: List[str]
    suggested_modifications: List[str]


class TradeAnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    direction: str = Field("LONG", description="'LONG' or 'SHORT'")
    thesis: str = Field(..., min_length=10, description="Trader rationale, setup hypothesis, and context")
    timeframe: str = Field("1d", pattern="^(1h|4h|1d|1w)$")
    entry_price: float = Field(..., gt=0.0)
    stop_loss: float = Field(..., gt=0.0)
    target_price: float = Field(..., gt=0.0)
    portfolio_equity: float = Field(100000.0, gt=0.0)
    risk_per_trade_pct: float = Field(1.0, ge=0.1, le=5.0)


class TradeAnalysisResponse(BaseModel):
    symbol: str
    direction: str
    thesis: str
    timeframe: str
    research: ResearchAgentOutput
    devils_advocate: DevilsAdvocateOutput
    risk: RiskCalculationResponse
    decision: DecisionAgentOutput
    execution_trace: Optional[List[Dict[str, Any]]] = Field(
        None, description="Ordered execution trace of tool and agent steps"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

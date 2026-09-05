from fastapi import APIRouter
from app.schemas.risk import RiskCalculationRequest, RiskCalculationResponse
from app.analysis.risk_engine import RiskEngine

router = APIRouter(prefix="/risk", tags=["Risk Management Engine"])


@router.post("/calculate", response_model=RiskCalculationResponse)
async def calculate_risk(req: RiskCalculationRequest):
    """
    Deterministic quantitative risk calculation endpoint.
    Performs:
    - Directional stop loss & target geometric validation (LONG vs SHORT)
    - 1% (or custom) position sizing based on portfolio equity and risk per share
    - Dynamic drawdown reduction scaling (10% DD -> 50% risk, 20% DD -> 25% risk)
    - Maximum portfolio exposure cap enforcement
    - Risk/Reward ratio calculation and threshold verification (>= 1.5)
    """
    return RiskEngine.calculate_risk(req)

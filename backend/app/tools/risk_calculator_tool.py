from app.tools.base import ToolResult, log_tool_execution
from app.schemas.risk import RiskCalculationRequest
from app.analysis.risk_engine import RiskEngine


@log_tool_execution("risk_calculator.calculate_position_size")
def calculate_position_size(
    symbol: str,
    direction: str,
    entry_price: float,
    stop_loss: float,
    target_price: float,
    portfolio_equity: float = 100000.0,
    risk_per_trade_pct: float = 1.0,
    current_drawdown_pct: float = 0.0,
    max_exposure_pct: float = 50.0,
) -> ToolResult:
    """Calculate optimal position size with full risk management using the deterministic RiskEngine."""
    try:
        req = RiskCalculationRequest(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            portfolio_equity=portfolio_equity,
            risk_per_trade_pct=risk_per_trade_pct,
            current_drawdown_pct=current_drawdown_pct,
            max_exposure_pct=max_exposure_pct,
        )
        result = RiskEngine.calculate_risk(req)
        return ToolResult(
            tool="risk_calculator.calculate_position_size",
            status="success",
            data=result.model_dump(),
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="risk_calculator.calculate_position_size",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("risk_calculator.calculate_risk_reward")
def calculate_risk_reward(
    entry_price: float,
    stop_loss: float,
    target_price: float,
    direction: str = "LONG",
) -> ToolResult:
    """Calculate risk/reward ratio and per-share metrics without full position sizing."""
    try:
        direction = direction.upper().strip()
        if direction == "LONG":
            risk_per_share = round(max(0.01, entry_price - stop_loss), 2)
            reward_per_share = round(max(0.01, target_price - entry_price), 2)
        elif direction == "SHORT":
            risk_per_share = round(max(0.01, stop_loss - entry_price), 2)
            reward_per_share = round(max(0.01, entry_price - target_price), 2)
        else:
            return ToolResult(
                tool="risk_calculator.calculate_risk_reward",
                status="error",
                data=None,
                error=f"Invalid direction '{direction}'. Must be LONG or SHORT.",
            )

        risk_reward_ratio = round(reward_per_share / risk_per_share, 2)
        return ToolResult(
            tool="risk_calculator.calculate_risk_reward",
            status="success",
            data={
                "direction": direction,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target_price": target_price,
                "risk_per_share": risk_per_share,
                "reward_per_share": reward_per_share,
                "risk_reward_ratio": risk_reward_ratio,
                "favorable": risk_reward_ratio >= 1.5,
            },
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="risk_calculator.calculate_risk_reward",
            status="error",
            data=None,
            error=str(e),
        )

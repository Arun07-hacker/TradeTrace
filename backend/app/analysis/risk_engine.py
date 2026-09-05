import math
from typing import List, Tuple
from app.schemas.risk import RiskCalculationRequest, RiskCalculationResponse


class RiskEngine:
    """
    Deterministic Financial Risk Management Engine.
    Executes strict quantitative sizing, geometric parameter validation,
    and portfolio preservation checks (No LLM heuristics).
    """

    @classmethod
    def calculate_risk(cls, req: RiskCalculationRequest) -> RiskCalculationResponse:
        direction = req.direction.upper().strip()
        entry = round(req.entry_price, 2)
        stop = round(req.stop_loss, 2)
        target = round(req.target_price, 2)
        equity = round(req.portfolio_equity, 2)
        configured_risk_pct = req.risk_per_trade_pct

        warnings: List[str] = []
        is_valid = True

        # 1. Geometric Validation
        if direction == "LONG":
            if stop >= entry:
                warnings.append("For a LONG trade, Stop Loss must be strictly below Entry Price.")
                is_valid = False
            if target <= entry:
                warnings.append("For a LONG trade, Target Price must be strictly above Entry Price.")
                is_valid = False
            risk_per_share = round(max(0.01, entry - stop), 2)
            reward_per_share = round(max(0.01, target - entry), 2)
        elif direction == "SHORT":
            if stop <= entry:
                warnings.append("For a SHORT trade, Stop Loss must be strictly above Entry Price.")
                is_valid = False
            if target >= entry:
                warnings.append("For a SHORT trade, Target Price must be strictly below Entry Price.")
                is_valid = False
            risk_per_share = round(max(0.01, stop - entry), 2)
            reward_per_share = round(max(0.01, entry - target), 2)
        else:
            warnings.append(f"Invalid direction '{direction}'. Must be LONG or SHORT.")
            is_valid = False
            risk_per_share = 1.0
            reward_per_share = 1.0

        # 2. Risk / Reward Ratio
        risk_reward_ratio = round(reward_per_share / risk_per_share, 2)
        if risk_reward_ratio < 1.5:
            warnings.append(f"Unfavorable Risk/Reward ratio (1:{risk_reward_ratio}). Minimum recommended threshold is 1:1.5.")

        # 3. Dynamic Drawdown Scaling (Capital Preservation Rule)
        effective_risk_pct = configured_risk_pct
        drawdown_adjusted = False
        if req.current_drawdown_pct >= 20.0:
            effective_risk_pct = configured_risk_pct * 0.25
            drawdown_adjusted = True
            warnings.append(f"Severe drawdown ({req.current_drawdown_pct}%): Risk scaled down 75% to {effective_risk_pct:.2f}% to protect capital.")
        elif req.current_drawdown_pct >= 10.0:
            effective_risk_pct = configured_risk_pct * 0.50
            drawdown_adjusted = True
            warnings.append(f"Cautionary drawdown ({req.current_drawdown_pct}%): Risk scaled down 50% to {effective_risk_pct:.2f}%.")

        # 4. Position Sizing
        risk_amount = round(equity * (effective_risk_pct / 100.0), 2)
        position_size = math.floor(risk_amount / risk_per_share) if risk_per_share > 0 else 0

        # 5. Portfolio Exposure
        position_value = round(position_size * entry, 2)
        portfolio_exposure = round(position_value / equity, 4) if equity > 0 else 0.0
        portfolio_exposure_pct = round(portfolio_exposure * 100.0, 1)

        if portfolio_exposure_pct > req.max_exposure_pct:
            warnings.append(f"Position exposure ({portfolio_exposure_pct}%) exceeds your max portfolio exposure cap of {req.max_exposure_pct}%.")
            # Downsize position to fit maximum exposure cap
            max_allowed_value = equity * (req.max_exposure_pct / 100.0)
            position_size = math.floor(max_allowed_value / entry) if entry > 0 else 0
            position_value = round(position_size * entry, 2)
            portfolio_exposure = round(position_value / equity, 4) if equity > 0 else 0.0
            portfolio_exposure_pct = round(portfolio_exposure * 100.0, 1)
            risk_amount = round(position_size * risk_per_share, 2)

        potential_reward = round(position_size * reward_per_share, 2)

        # 6. Risk Level Categorization
        if not is_valid or risk_reward_ratio < 1.0 or portfolio_exposure_pct > req.max_exposure_pct:
            risk_level = "excessive"
        elif risk_reward_ratio < 1.5 or portfolio_exposure_pct > 35.0:
            risk_level = "aggressive"
        elif effective_risk_pct <= 1.0 and risk_reward_ratio >= 2.0 and portfolio_exposure_pct <= 25.0:
            risk_level = "conservative"
        else:
            risk_level = "moderate"

        return RiskCalculationResponse(
            symbol=req.symbol.upper(),
            direction=direction,
            entry_price=entry,
            stop_loss=stop,
            target=target,
            risk_per_share=risk_per_share,
            reward_per_share=reward_per_share,
            risk_amount=risk_amount,
            potential_reward=potential_reward,
            position_size=position_size,
            risk_reward_ratio=risk_reward_ratio,
            position_value=position_value,
            portfolio_exposure=portfolio_exposure,
            portfolio_exposure_pct=portfolio_exposure_pct,
            risk_level=risk_level,
            is_valid=is_valid,
            warnings=warnings,
            drawdown_adjusted=drawdown_adjusted,
        )

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas.risk import RiskCalculationRequest
from app.analysis.risk_engine import RiskEngine



def test_risk_engine_valid_long():
    req = RiskCalculationRequest(
        symbol="AAPL",
        direction="LONG",
        entry_price=150.0,
        stop_loss=145.0,
        target_price=165.0,
        portfolio_equity=100000.0,
        risk_per_trade_pct=1.0,
    )
    res = RiskEngine.calculate_risk(req)
    assert res.is_valid is True
    assert res.risk_per_share == 5.0
    assert res.reward_per_share == 15.0
    assert res.risk_reward_ratio == 3.0
    assert res.risk_amount == 1000.0
    assert res.position_size == 200  # 1000 / 5
    assert res.potential_reward == 3000.0  # 200 * 15
    assert res.position_value == 30000.0  # 200 * 150
    assert res.portfolio_exposure_pct == 30.0
    assert res.drawdown_adjusted is False
    assert res.risk_level in ["conservative", "moderate"]


def test_risk_engine_valid_short():
    req = RiskCalculationRequest(
        symbol="TSLA",
        direction="SHORT",
        entry_price=200.0,
        stop_loss=210.0,
        target_price=170.0,
        portfolio_equity=50000.0,
        risk_per_trade_pct=1.0,
    )
    res = RiskEngine.calculate_risk(req)
    assert res.is_valid is True
    assert res.risk_per_share == 10.0
    assert res.reward_per_share == 30.0
    assert res.risk_reward_ratio == 3.0
    assert res.risk_amount == 500.0
    assert res.position_size == 50  # 500 / 10
    assert res.potential_reward == 1500.0


def test_risk_engine_invalid_geometry_long():
    # Stop loss above entry for LONG
    req = RiskCalculationRequest(
        symbol="MSFT",
        direction="LONG",
        entry_price=300.0,
        stop_loss=305.0,
        target_price=320.0,
    )
    res = RiskEngine.calculate_risk(req)
    assert res.is_valid is False
    assert any("Stop Loss must be strictly below Entry" in w for w in res.warnings)
    assert res.risk_level == "excessive"


def test_risk_engine_invalid_geometry_short():
    # Target above entry for SHORT
    req = RiskCalculationRequest(
        symbol="NVDA",
        direction="SHORT",
        entry_price=120.0,
        stop_loss=125.0,
        target_price=130.0,
    )
    res = RiskEngine.calculate_risk(req)
    assert res.is_valid is False
    assert any("Target Price must be strictly below Entry" in w for w in res.warnings)


def test_risk_engine_drawdown_scaling():
    # 10% drawdown cuts risk by 50%
    req10 = RiskCalculationRequest(
        symbol="AAPL",
        direction="LONG",
        entry_price=100.0,
        stop_loss=95.0,
        target_price=115.0,
        portfolio_equity=100000.0,
        risk_per_trade_pct=1.0,
        current_drawdown_pct=12.0,
    )
    res10 = RiskEngine.calculate_risk(req10)
    assert res10.drawdown_adjusted is True
    assert res10.risk_amount == 500.0  # 0.5% of 100k
    assert res10.position_size == 100  # 500 / 5

    # 20% drawdown cuts risk by 75%
    req20 = RiskCalculationRequest(
        symbol="AAPL",
        direction="LONG",
        entry_price=100.0,
        stop_loss=95.0,
        target_price=115.0,
        portfolio_equity=100000.0,
        risk_per_trade_pct=1.0,
        current_drawdown_pct=22.0,
    )
    res20 = RiskEngine.calculate_risk(req20)
    assert res20.drawdown_adjusted is True
    assert res20.risk_amount == 250.0  # 0.25% of 100k
    assert res20.position_size == 50  # 250 / 5


def test_risk_engine_exposure_cap_clamping():
    # Very tight stop (0.50 risk per share) with $1000 risk budget = 2000 shares
    # 2000 shares * $100 entry = $200,000 (200% exposure), exceeds 50% cap ($50,000)
    req = RiskCalculationRequest(
        symbol="AAPL",
        direction="LONG",
        entry_price=100.0,
        stop_loss=99.50,
        target_price=110.0,
        portfolio_equity=100000.0,
        risk_per_trade_pct=1.0,
        max_exposure_pct=50.0,
    )
    res = RiskEngine.calculate_risk(req)
    assert res.portfolio_exposure_pct <= 50.0
    assert res.position_size == 500  # 50,000 / 100
    assert res.position_value == 50000.0
    assert any("exceeds your max portfolio exposure cap" in w for w in res.warnings)


@pytest.mark.asyncio

async def test_api_risk_calculate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "symbol": "AAPL",
            "direction": "LONG",
            "entry_price": 150.0,
            "stop_loss": 145.0,
            "target_price": 165.0,
            "portfolio_equity": 100000.0,
            "risk_per_trade_pct": 1.0,
            "current_drawdown_pct": 0.0,
            "max_exposure_pct": 50.0,
        }
        response = await client.post("/api/v1/risk/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["position_size"] == 200
    assert data["risk_reward_ratio"] == 3.0
    assert data["is_valid"] is True


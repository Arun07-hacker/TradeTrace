import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db, init_db


@pytest.fixture
async def paper_client():
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    await init_db(test_engine)
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_paper_trading_lifecycle(paper_client: AsyncClient):
    # 1. Register & login
    email = f"trader_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await paper_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "name": "Paper Trader",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check initial portfolio balance ($100,000)
    port_resp = await paper_client.get("/api/v1/portfolio", headers=headers)
    assert port_resp.status_code == 200
    portfolio = port_resp.json()
    assert portfolio["cash_balance"] == 100000.0
    assert portfolio["total_equity"] == 100000.0
    assert len(portfolio["positions"]) == 0

    # 3. Test Insufficient Funds Protection
    huge_order = {
        "symbol": "AAPL",
        "direction": "LONG",
        "timeframe": "1d",
        "entry_price": 150.0,
        "stop_loss": 140.0,
        "target": 170.0,
        "quantity": 1000.0,  # 1000 * 150 = $150,000 > $100,000 cash
        "thesis": "Oversized breakout attempt",
        "decision": "PROCEED_WITH_CAUTION",
    }
    fail_resp = await paper_client.post("/api/v1/trades", json=huge_order, headers=headers)
    assert fail_resp.status_code == 400
    assert "Insufficient paper cash" in fail_resp.json()["detail"]

    # 4. Execute a valid Paper Trade (100 shares @ $150 = $15,000)
    valid_order = {
        "symbol": "AAPL",
        "direction": "LONG",
        "timeframe": "1d",
        "entry_price": 150.0,
        "stop_loss": 145.0,
        "target": 165.0,
        "quantity": 100.0,
        "thesis": "Ascending triangle breakout above $150 resistance with volume surge",
        "decision": "PROCEED_WITH_CAUTION",
    }
    trade_resp = await paper_client.post("/api/v1/trades", json=valid_order, headers=headers)
    assert trade_resp.status_code == 201
    trade = trade_resp.json()
    trade_id = trade["id"]
    assert trade["symbol"] == "AAPL"
    assert trade["status"] == "OPEN"
    assert trade["risk_amount"] == 500.0  # 100 * (150 - 145)
    assert trade["risk_reward_ratio"] == 3.0  # (165 - 150) / 5
    assert len(trade["events"]) >= 1

    # 5. Verify portfolio cash was deducted and position exists
    port_resp2 = await paper_client.get("/api/v1/portfolio", headers=headers)
    p2 = port_resp2.json()
    assert p2["cash_balance"] == 85000.0  # 100,000 - 15,000
    assert len(p2["positions"]) == 1
    assert p2["positions"][0]["symbol"] == "AAPL"

    # 6. List trades
    list_resp = await paper_client.get("/api/v1/trades?status=OPEN", headers=headers)
    assert list_resp.status_code == 200
    open_trades = list_resp.json()
    assert len(open_trades) == 1
    assert open_trades[0]["id"] == trade_id

    # 7. Get trade detail by ID
    get_resp = await paper_client.get(f"/api/v1/trades/{trade_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == trade_id

    # 8. Close the trade at Target ($165.00 -> Profit = ($165 - $150) * 100 = +$1,500)
    close_payload = {
        "exit_price": 165.0,
        "reason": "TARGET_HIT",
    }
    close_resp = await paper_client.post(
        f"/api/v1/trades/{trade_id}/close", json=close_payload, headers=headers
    )
    assert close_resp.status_code == 200
    closed_trade = close_resp.json()
    assert closed_trade["status"] == "TARGET_HIT"
    assert closed_trade["realized_pnl"] == 1500.0
    assert closed_trade["realized_pnl_pct"] == 10.0
    assert closed_trade["exit_price"] == 165.0

    # 9. Verify Portfolio reflect profit
    port_resp3 = await paper_client.get("/api/v1/portfolio", headers=headers)
    p3 = port_resp3.json()
    assert p3["cash_balance"] == 101500.0  # 85,000 + 15,000 principal + 1,500 profit
    assert p3["total_equity"] == 101500.0
    assert p3["realized_pnl"] == 1500.0
    assert p3["win_count"] == 1
    assert p3["loss_count"] == 0
    assert len(p3["positions"]) == 0

    # 10. Test Portfolio Reset
    reset_resp = await paper_client.post("/api/v1/portfolio/reset", headers=headers)
    assert reset_resp.status_code == 200
    p_reset = reset_resp.json()
    assert p_reset["cash_balance"] == 100000.0
    assert p_reset["realized_pnl"] == 0.0
    assert p_reset["win_count"] == 0

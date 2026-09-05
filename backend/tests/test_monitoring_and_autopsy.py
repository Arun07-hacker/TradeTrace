import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db, init_db


@pytest.fixture
async def monitor_client():
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
async def test_monitoring_and_autopsy_full_cycle(monitor_client: AsyncClient):
    # 1. Register & Login
    email = f"autopsy_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await monitor_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "name": "Autopsy Test Trader",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Place a paper trade
    # Note: Current mock price for AAPL is around 220. We set stop_loss to 250 (which is above current price for LONG)
    # to simulate the price having broken through the stop loss.
    trade_order = {
        "symbol": "AAPL",
        "direction": "LONG",
        "timeframe": "1d",
        "entry_price": 260.0,
        "stop_loss": 250.0,
        "target": 290.0,
        "quantity": 10.0,
        "thesis": "Bullish breakout above 260 consolidation",
        "decision": "PROCEED_WITH_CAUTION",
    }
    trade_resp = await monitor_client.post("/api/v1/trades", json=trade_order, headers=headers)
    assert trade_resp.status_code == 201
    trade_data = trade_resp.json()
    trade_id = trade_data["id"]
    assert trade_data["status"] == "OPEN"

    # 3. Run Monitoring Check -> Should detect current price (approx 220) is <= stop_loss (250)
    check_resp = await monitor_client.post("/api/v1/monitoring/check-now", headers=headers)
    assert check_resp.status_code == 200
    check_data = check_resp.json()
    assert check_data["checked_trades_count"] >= 1
    assert check_data["alerts_created_count"] >= 1

    # 4. Verify Trade status transitioned to STOP_HIT
    get_trade = await monitor_client.get(f"/api/v1/trades/{trade_id}", headers=headers)
    assert get_trade.status_code == 200
    updated_trade = get_trade.json()
    assert updated_trade["status"] == "STOP_HIT"
    assert updated_trade["realized_pnl"] is not None

    # 5. Verify Alert was logged and mark it as read
    alerts_resp = await monitor_client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]
    assert alerts[0]["alert_type"] == "STOP_LOSS_HIT"
    assert alerts[0]["is_read"] is False

    read_resp = await monitor_client.post(f"/api/v1/alerts/{alert_id}/read", headers=headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # 6. Run Post-Trade Autopsy Agent
    autopsy_payload = {
        "trader_notes": "Entered late after market had already rallied 4 days without resting."
    }
    autopsy_resp = await monitor_client.post(
        f"/api/v1/trades/{trade_id}/autopsy", json=autopsy_payload, headers=headers
    )
    assert autopsy_resp.status_code == 200
    autopsy_data = autopsy_resp.json()
    assert autopsy_data["trade_id"] == trade_id
    assert autopsy_data["outcome"] == "LOSS"
    assert autopsy_data["key_mistake"] != ""
    assert autopsy_data["lesson_learned"] != ""
    assert autopsy_data["future_rule"] != ""
    assert autopsy_data["indexed_in_memory"] is True

    # 7. Search Trading Memory to confirm the learned lesson is now in vector memory!
    search_resp = await monitor_client.get(
        "/api/v1/memory/search",
        params={"q": "breakout consolidation stop loss failure", "limit": 5},
        headers=headers,
    )
    assert search_resp.status_code == 200
    search_results = search_resp.json()
    assert search_results["total_results"] > 0
    # Confirm our newly saved lesson or trade memory appears in results
    assert any(
        "AAPL" in r.get("title", "") or "AAPL" in (r.get("symbol") or "") or "breakout" in r.get("content", "").lower()
        for r in search_results["results"]
    )

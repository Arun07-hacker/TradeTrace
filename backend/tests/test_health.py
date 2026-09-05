import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == settings.APP_NAME
    assert data["status"] == "operational"
    assert data["demo_mode"] is True


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert "providers" in data
    assert data["providers"]["llm"] == "mock"
    assert data["providers"]["market_data"] == "mock"
    assert data["providers"]["news"] == "mock"

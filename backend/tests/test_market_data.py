import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.market_data.mock_provider import MockMarketDataProvider
from app.services.market_data.factory import get_market_data_provider


@pytest.fixture
def mock_provider():
    return MockMarketDataProvider(seed=123)


@pytest.fixture
async def api_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_mock_provider_supported_symbols(mock_provider: MockMarketDataProvider):
    symbols = await mock_provider.get_supported_symbols()
    assert len(symbols) >= 4
    ticker_set = {s.symbol for s in symbols}
    for expected in ["AAPL", "MSFT", "NVDA", "TSLA"]:
        assert expected in ticker_set
    for s in symbols:
        assert s.current_price > 0
        assert s.is_demo is True


@pytest.mark.asyncio
async def test_mock_provider_latest_quote(mock_provider: MockMarketDataProvider):
    quote = await mock_provider.get_latest_quote("AAPL")
    assert quote.symbol == "AAPL"
    assert quote.price > 150.0
    assert quote.high_24h >= quote.price
    assert quote.low_24h <= quote.price
    assert quote.volume > 1000000
    assert quote.is_demo is True


@pytest.mark.asyncio
async def test_mock_provider_candlestick_consistency(mock_provider: MockMarketDataProvider):
    limit = 60
    bars = await mock_provider.get_historical_bars("NVDA", timeframe="1d", limit=limit)
    assert len(bars) == limit

    for b in bars:
        # High must be >= both open and close
        assert b.high >= b.open - 1e-6
        assert b.high >= b.close - 1e-6
        # Low must be <= both open and close
        assert b.low <= b.open + 1e-6
        assert b.low <= b.close + 1e-6
        # Volume must be positive
        assert b.volume > 0


@pytest.mark.asyncio
async def test_mock_provider_timeframes(mock_provider: MockMarketDataProvider):
    for tf in ["1h", "4h", "1d", "1w"]:
        bars = await mock_provider.get_historical_bars("TSLA", timeframe=tf, limit=20)
        assert len(bars) == 20


@pytest.mark.asyncio
async def test_api_market_symbols_endpoint(api_client: AsyncClient):
    response = await api_client.get("/api/v1/market/symbols")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    symbols = [item["symbol"] for item in data]
    assert "AAPL" in symbols


@pytest.mark.asyncio
async def test_api_market_quote_endpoint(api_client: AsyncClient):
    response = await api_client.get("/api/v1/market/MSFT")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "MSFT"
    assert data["price"] > 300.0
    assert data["is_demo"] is True


@pytest.mark.asyncio
async def test_api_market_history_endpoint(api_client: AsyncClient):
    response = await api_client.get("/api/v1/market/AAPL/history?timeframe=1d&limit=45")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["timeframe"] == "1d"
    assert data["count"] == 45
    assert len(data["bars"]) == 45
    assert data["is_demo"] is True


@pytest.mark.asyncio
async def test_api_invalid_timeframe_rejected(api_client: AsyncClient):
    response = await api_client.get("/api/v1/market/AAPL/history?timeframe=invalid_tf")
    assert response.status_code == 422

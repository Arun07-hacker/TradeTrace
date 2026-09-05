import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.news.mock_provider import MockNewsProvider


@pytest.fixture
def news_provider():
    return MockNewsProvider()


@pytest.fixture
async def api_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_mock_news_provider_articles(news_provider: MockNewsProvider):
    """Verify news normalization and scoring."""
    articles = await news_provider.get_news_for_symbol("AAPL", limit=5)
    assert len(articles) > 0

    for item in articles:
        assert item.symbol == "AAPL"
        assert len(item.title) > 5
        assert len(item.description) > 10
        assert item.source is not None
        assert item.sentiment in ["BULLISH", "BEARISH", "NEUTRAL"]
        assert -1.0 <= item.sentiment_score <= 1.0
        assert item.relevance in ["HIGH", "MEDIUM", "LOW"]
        assert 0.0 <= item.relevance_score <= 1.0
        assert item.event_type in ["EARNINGS", "PRODUCT", "REGULATORY", "MACRO", "ANALYST", "GENERAL"]
        assert item.impact in ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.asyncio
async def test_news_deduplication(news_provider: MockNewsProvider):
    """Verify that articles returned contain no duplicate titles or URLs."""
    articles = await news_provider.get_news_for_symbol("NVDA", limit=10)
    titles = [a.title.lower() for a in articles]
    urls = [a.url.lower() for a in articles]

    assert len(titles) == len(set(titles)), "Duplicate article title found"
    assert len(urls) == len(set(urls)), "Duplicate article URL found"


@pytest.mark.asyncio
async def test_mock_news_provider_upcoming_events(news_provider: MockNewsProvider):
    """Verify catalyst event detection (e.g. Earnings, FOMC)."""
    events = await news_provider.get_upcoming_events_for_symbol("AAPL")
    assert len(events) >= 1

    event_types = [e.event_type for e in events]
    assert "EARNINGS" in event_types

    earnings_event = next(e for e in events if e.event_type == "EARNINGS")
    assert earnings_event.days_until > 0
    assert earnings_event.impact == "HIGH"
    assert "volatility" in earnings_event.implied_volatility_effect.lower()


@pytest.mark.asyncio
async def test_generic_symbol_news_fallback(news_provider: MockNewsProvider):
    """Verify graceful fallback for unlisted symbol."""
    articles = await news_provider.get_news_for_symbol("GOOGL", limit=2)
    assert len(articles) >= 1
    assert articles[0].symbol == "GOOGL"


@pytest.mark.asyncio
async def test_api_news_endpoint(api_client: AsyncClient):
    """Test REST API GET /api/v1/news/TSLA."""
    response = await api_client.get("/api/v1/news/TSLA?limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "TSLA"
    assert data["count"] > 0
    assert len(data["articles"]) > 0
    assert data["is_demo"] is True
    assert "sentiment" in data["articles"][0]


@pytest.mark.asyncio
async def test_api_events_endpoint(api_client: AsyncClient):
    """Test REST API GET /api/v1/news/AAPL/events."""
    response = await api_client.get("/api/v1/news/AAPL/events")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["count"] > 0
    assert len(data["events"]) > 0
    assert data["is_demo"] is True
    assert data["events"][0]["days_until"] > 0

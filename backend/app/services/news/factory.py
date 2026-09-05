from app.core.config import settings
from app.services.news.base import NewsProvider
from app.services.news.mock_provider import MockNewsProvider

_cached_news_provider: NewsProvider = None


def get_news_provider() -> NewsProvider:
    """
    Factory function returning the configured news provider.
    Defaults to MockNewsProvider for offline/demo operation.
    """
    global _cached_news_provider
    if _cached_news_provider is not None:
        return _cached_news_provider

    provider_name = settings.NEWS_PROVIDER.lower().strip()
    if provider_name == "mock":
        _cached_news_provider = MockNewsProvider()
    else:
        # Fallback to MockNewsProvider if external API keys not supplied
        _cached_news_provider = MockNewsProvider()

    return _cached_news_provider

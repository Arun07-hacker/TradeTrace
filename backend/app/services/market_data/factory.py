from app.core.config import settings
from app.services.market_data.base import MarketDataProvider
from app.services.market_data.mock_provider import MockMarketDataProvider

_cached_provider: MarketDataProvider = None


def get_market_data_provider() -> MarketDataProvider:
    """
    Factory function returning the configured market data provider.
    Defaults to MockMarketDataProvider if configured or for demo mode.
    """
    global _cached_provider
    if _cached_provider is not None:
        return _cached_provider

    provider_type = settings.MARKET_DATA_PROVIDER.lower().strip()
    if provider_type == "mock":
        _cached_provider = MockMarketDataProvider()
    else:
        # Fallback to Mock provider for unconfigured vendor keys
        _cached_provider = MockMarketDataProvider()

    return _cached_provider

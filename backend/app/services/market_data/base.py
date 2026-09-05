from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.market import MarketQuote, OHLCVBar, SymbolInfo


class MarketDataProvider(ABC):
    """
    Abstract interface for market data providers.
    Decouples TradeTrace from specific data vendors (e.g. Polygon, AlphaVantage, Yahoo, or Mock).
    """

    @abstractmethod
    async def get_latest_quote(self, symbol: str) -> MarketQuote:
        """Fetch the latest price quote for a given symbol."""
        pass

    @abstractmethod
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100,
    ) -> List[OHLCVBar]:
        """Fetch historical OHLCV candlestick bars for a given symbol and timeframe."""
        pass

    @abstractmethod
    async def get_supported_symbols(self) -> List[SymbolInfo]:
        """Fetch supported watchlist symbols with latest overview metrics."""
        pass

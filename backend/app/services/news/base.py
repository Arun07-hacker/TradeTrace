from abc import ABC, abstractmethod
from typing import List
from app.schemas.news import NewsArticleItem, MarketEventItem


class NewsProvider(ABC):
    """
    Abstract interface for financial news and market event providers.
    Allows swappable implementations (e.g. Finnhub, NewsAPI, AlphaVantage, or Mock).
    """

    @abstractmethod
    async def get_news_for_symbol(self, symbol: str, limit: int = 10) -> List[NewsArticleItem]:
        """Fetch latest deduplicated news articles with sentiment and relevance metadata."""
        pass

    @abstractmethod
    async def get_upcoming_events_for_symbol(self, symbol: str) -> List[MarketEventItem]:
        """Fetch high-impact scheduled catalyst events (e.g. Earnings, FOMC, Key Launches)."""
        pass

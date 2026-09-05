from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class NewsArticleItem(BaseModel):
    symbol: str = Field(..., description="Target asset ticker symbol")
    title: str = Field(..., description="Headline of the news article")
    description: str = Field(..., description="Summary of the article content")
    source: str = Field(..., description="News agency or publication source")
    url: str = Field(..., description="Article URL or source identifier")
    published_at: datetime = Field(..., description="Publication UTC timestamp")
    sentiment: str = Field(..., description="Sentiment classification: BULLISH, BEARISH, or NEUTRAL")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score from -1.0 (bearish) to 1.0 (bullish)")
    relevance: str = Field(..., description="Relevance classification: HIGH, MEDIUM, or LOW")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score from 0.0 to 1.0")
    event_type: str = Field(..., description="Event type: EARNINGS, MACRO, PRODUCT, REGULATORY, ANALYST, GENERAL")
    impact: str = Field(..., description="Estimated market impact: HIGH, MEDIUM, or LOW")


class NewsResponse(BaseModel):
    symbol: str
    count: int
    articles: List[NewsArticleItem]
    is_demo: bool = True


class MarketEventItem(BaseModel):
    event_id: str
    symbol: str
    title: str
    event_type: str  # EARNINGS, FOMC, CPI, PRODUCT_LAUNCH, DIVIDEND
    event_date: datetime
    days_until: int
    impact: str  # HIGH, MEDIUM, LOW
    description: str
    implied_volatility_effect: str


class MarketEventsResponse(BaseModel):
    symbol: str
    count: int
    events: List[MarketEventItem]
    is_demo: bool = True

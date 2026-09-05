from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.news import NewsResponse, MarketEventsResponse
from app.services.news.factory import get_news_provider
from app.services.news.base import NewsProvider

router = APIRouter(prefix="/news", tags=["News & Market Events"])


@router.get("/{symbol}", response_model=NewsResponse)
async def get_symbol_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=50, description="Max news articles to return"),
    news_provider: NewsProvider = Depends(get_news_provider),
):
    """
    Retrieve normalized, deduplicated financial news for a symbol.
    Includes sentiment score (-1.0 to 1.0), relevance score, event type, and estimated impact.
    """
    sym = symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")

    articles = await news_provider.get_news_for_symbol(sym, limit=limit)
    return NewsResponse(
        symbol=sym,
        count=len(articles),
        articles=articles,
        is_demo=True,
    )


@router.get("/{symbol}/events", response_model=MarketEventsResponse)
async def get_symbol_events(
    symbol: str,
    news_provider: NewsProvider = Depends(get_news_provider),
):
    """
    Retrieve upcoming high-impact market catalysts (e.g. Earnings, FOMC rate decisions).
    Identifies event risk that could invalidate breakout or momentum setups.
    """
    sym = symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")

    events = await news_provider.get_upcoming_events_for_symbol(sym)
    return MarketEventsResponse(
        symbol=sym,
        count=len(events),
        events=events,
        is_demo=True,
    )

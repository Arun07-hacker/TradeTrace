from app.tools.base import ToolResult, log_tool_execution
from app.services.news.factory import get_news_provider


@log_tool_execution("news_search.search_news")
async def search_news(symbol: str, limit: int = 5) -> ToolResult:
    """Search recent financial news articles for a given symbol."""
    try:
        provider = get_news_provider()
        articles = await provider.get_news_for_symbol(symbol, limit=limit)
        articles_data = [a.model_dump() if hasattr(a, "model_dump") else a for a in articles]
        return ToolResult(
            tool="news_search.search_news",
            status="success",
            data=articles_data,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="news_search.search_news",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("news_search.get_market_events")
async def get_market_events(symbol: str) -> ToolResult:
    """Fetch upcoming catalyst events (earnings, FOMC, product launches) for a symbol."""
    try:
        provider = get_news_provider()
        events = await provider.get_upcoming_events_for_symbol(symbol)
        events_data = [e.model_dump() if hasattr(e, "model_dump") else e for e in events]
        return ToolResult(
            tool="news_search.get_market_events",
            status="success",
            data=events_data,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="news_search.get_market_events",
            status="error",
            data=None,
            error=str(e),
        )

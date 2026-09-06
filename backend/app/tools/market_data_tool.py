from typing import Optional
from app.tools.base import ToolResult, log_tool_execution
from app.services.market_data.factory import get_market_data_provider


@log_tool_execution("market_data.get_market_data")
async def get_market_data(symbol: str) -> ToolResult:
    """Fetch real-time / latest market quote for symbol."""
    try:
        provider = get_market_data_provider()
        quote = await provider.get_latest_quote(symbol)
        return ToolResult(
            tool="market_data.get_market_data",
            status="success",
            data=quote.model_dump() if hasattr(quote, "model_dump") else quote,
            error=None
        )
    except Exception as e:
        return ToolResult(
            tool="market_data.get_market_data",
            status="error",
            data=None,
            error=str(e)
        )


@log_tool_execution("market_data.get_historical_market_data")
async def get_historical_market_data(symbol: str, timeframe: str = "1d", limit: int = 100) -> ToolResult:
    """Fetch historical OHLCV candlestick bars for symbol."""
    try:
        provider = get_market_data_provider()
        bars = await provider.get_historical_bars(symbol, timeframe=timeframe, limit=limit)
        bars_data = [b.model_dump() if hasattr(b, "model_dump") else b for b in bars]
        return ToolResult(
            tool="market_data.get_historical_market_data",
            status="success",
            data=bars_data,
            error=None
        )
    except Exception as e:
        return ToolResult(
            tool="market_data.get_historical_market_data",
            status="error",
            data=None,
            error=str(e)
        )

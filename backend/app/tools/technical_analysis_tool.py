from app.tools.base import ToolResult, log_tool_execution
from app.services.market_data.factory import get_market_data_provider
from app.analysis.engine import TechnicalAnalysisEngine


@log_tool_execution("technical_analysis.calculate_indicators")
async def calculate_indicators(symbol: str, timeframe: str = "1d", limit: int = 100) -> ToolResult:
    """Calculate technical analysis indicators (SMA, EMA, RSI, MACD, ATR, Volatility, S/R levels)."""
    try:
        provider = get_market_data_provider()
        bars = await provider.get_historical_bars(symbol, timeframe=timeframe, limit=limit)
        res = TechnicalAnalysisEngine.analyze(symbol, bars, is_demo=True)
        return ToolResult(
            tool="technical_analysis.calculate_indicators",
            status="success",
            data=res.model_dump() if hasattr(res, "model_dump") else res,
            error=None
        )
    except Exception as e:
        return ToolResult(
            tool="technical_analysis.calculate_indicators",
            status="error",
            data=None,
            error=str(e)
        )


@log_tool_execution("technical_analysis.analyze_trend")
async def analyze_trend(symbol: str, timeframe: str = "1d", limit: int = 100) -> ToolResult:
    """Analyze current trend direction, strength, and support/resistance levels."""
    try:
        provider = get_market_data_provider()
        bars = await provider.get_historical_bars(symbol, timeframe=timeframe, limit=limit)
        res = TechnicalAnalysisEngine.analyze(symbol, bars, is_demo=True)
        trend_summary = {
            "symbol": res.symbol,
            "current_price": res.current_price,
            "trend": res.trend,
            "trend_details": res.trend_details.model_dump() if hasattr(res.trend_details, "model_dump") else res.trend_details,
            "rsi": res.rsi,
            "support_resistance": res.support_resistance.model_dump() if hasattr(res.support_resistance, "model_dump") else res.support_resistance,
            "volume_signal": res.volume_signal,
        }
        return ToolResult(
            tool="technical_analysis.analyze_trend",
            status="success",
            data=trend_summary,
            error=None
        )
    except Exception as e:
        return ToolResult(
            tool="technical_analysis.analyze_trend",
            status="error",
            data=None,
            error=str(e)
        )

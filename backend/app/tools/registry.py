"""
TradeTrace Tool Registry.
Central catalog of all agent-callable tools with metadata for discovery.
"""
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

from app.tools import market_data_tool
from app.tools import technical_analysis_tool
from app.tools import news_search_tool
from app.tools import memory_search_tool
from app.tools import risk_calculator_tool
from app.tools import portfolio_tool
from app.tools import paper_trade_tool
from app.tools import alert_tool
from app.tools import trade_history_tool


@dataclass
class ToolDefinition:
    """Metadata describing a registered tool function."""
    name: str
    description: str
    function: Callable
    requires_db: bool = False
    requires_user: bool = False
    category: str = "general"
    parameters: List[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
# Tool Registry
# ──────────────────────────────────────────────────────────────────

TOOLS: Dict[str, ToolDefinition] = {
    # ── Market Data ──
    "market_data.get_market_data": ToolDefinition(
        name="market_data.get_market_data",
        description="Fetch real-time / latest market quote for a symbol.",
        function=market_data_tool.get_market_data,
        category="market_data",
        parameters=["symbol"],
    ),
    "market_data.get_historical_market_data": ToolDefinition(
        name="market_data.get_historical_market_data",
        description="Fetch historical OHLCV candlestick bars for a symbol.",
        function=market_data_tool.get_historical_market_data,
        category="market_data",
        parameters=["symbol", "timeframe", "limit"],
    ),

    # ── Technical Analysis ──
    "technical_analysis.calculate_indicators": ToolDefinition(
        name="technical_analysis.calculate_indicators",
        description="Calculate full technical analysis indicators (SMA, EMA, RSI, MACD, ATR, S/R levels).",
        function=technical_analysis_tool.calculate_indicators,
        category="technical_analysis",
        parameters=["symbol", "timeframe", "limit"],
    ),
    "technical_analysis.analyze_trend": ToolDefinition(
        name="technical_analysis.analyze_trend",
        description="Analyze current trend direction, strength, and key levels.",
        function=technical_analysis_tool.analyze_trend,
        category="technical_analysis",
        parameters=["symbol", "timeframe", "limit"],
    ),

    # ── News Search ──
    "news_search.search_news": ToolDefinition(
        name="news_search.search_news",
        description="Search recent financial news articles for a symbol.",
        function=news_search_tool.search_news,
        category="news_search",
        parameters=["symbol", "limit"],
    ),
    "news_search.get_market_events": ToolDefinition(
        name="news_search.get_market_events",
        description="Fetch upcoming catalyst events (earnings, FOMC, product launches).",
        function=news_search_tool.get_market_events,
        category="news_search",
        parameters=["symbol"],
    ),

    # ── Memory Search ──
    "memory_search.search_similar_trades": ToolDefinition(
        name="memory_search.search_similar_trades",
        description="Search trading memory for historically similar trade setups.",
        function=memory_search_tool.search_similar_trades,
        requires_db=True,
        requires_user=True,
        category="memory_search",
        parameters=["db", "user_id", "thesis", "symbol", "top_k"],
    ),
    "memory_search.get_previous_lessons": ToolDefinition(
        name="memory_search.get_previous_lessons",
        description="Retrieve relevant trading lessons from the cognitive memory vault.",
        function=memory_search_tool.get_previous_lessons,
        requires_db=True,
        requires_user=True,
        category="memory_search",
        parameters=["db", "user_id", "thesis", "top_k"],
    ),

    # ── Risk Calculator ──
    "risk_calculator.calculate_position_size": ToolDefinition(
        name="risk_calculator.calculate_position_size",
        description="Calculate optimal position size with full risk management.",
        function=risk_calculator_tool.calculate_position_size,
        category="risk_calculator",
        parameters=["symbol", "direction", "entry_price", "stop_loss", "target_price",
                     "portfolio_equity", "risk_per_trade_pct"],
    ),
    "risk_calculator.calculate_risk_reward": ToolDefinition(
        name="risk_calculator.calculate_risk_reward",
        description="Calculate risk/reward ratio and per-share metrics.",
        function=risk_calculator_tool.calculate_risk_reward,
        category="risk_calculator",
        parameters=["entry_price", "stop_loss", "target_price", "direction"],
    ),

    # ── Portfolio ──
    "portfolio.get_portfolio": ToolDefinition(
        name="portfolio.get_portfolio",
        description="Retrieve full paper trading portfolio summary with positions.",
        function=portfolio_tool.get_portfolio,
        requires_db=True,
        requires_user=True,
        category="portfolio",
        parameters=["db", "user_id"],
    ),
    "portfolio.get_open_positions": ToolDefinition(
        name="portfolio.get_open_positions",
        description="List all currently open paper trading positions.",
        function=portfolio_tool.get_open_positions,
        requires_db=True,
        requires_user=True,
        category="portfolio",
        parameters=["db", "user_id"],
    ),

    # ── Paper Trade ──
    "paper_trade.create_paper_trade": ToolDefinition(
        name="paper_trade.create_paper_trade",
        description="Execute a new paper trade.",
        function=paper_trade_tool.create_paper_trade,
        requires_db=True,
        requires_user=True,
        category="paper_trade",
        parameters=["db", "user_id", "symbol", "direction", "entry_price",
                     "stop_loss", "target", "quantity", "thesis", "decision"],
    ),
    "paper_trade.close_paper_trade": ToolDefinition(
        name="paper_trade.close_paper_trade",
        description="Close an existing open paper trade.",
        function=paper_trade_tool.close_paper_trade,
        requires_db=True,
        requires_user=True,
        category="paper_trade",
        parameters=["db", "user_id", "trade_id", "exit_price", "reason"],
    ),

    # ── Alert ──
    "alert.create_alert": ToolDefinition(
        name="alert.create_alert",
        description="Create a new alert notification for the user.",
        function=alert_tool.create_alert,
        requires_db=True,
        requires_user=True,
        category="alert",
        parameters=["db", "user_id", "symbol", "alert_type", "title", "message", "severity"],
    ),
    "alert.get_alerts": ToolDefinition(
        name="alert.get_alerts",
        description="Retrieve alerts for a user.",
        function=alert_tool.get_alerts,
        requires_db=True,
        requires_user=True,
        category="alert",
        parameters=["db", "user_id", "unread_only"],
    ),

    # ── Trade History ──
    "trade_history.get_trade_history": ToolDefinition(
        name="trade_history.get_trade_history",
        description="Retrieve paper trade history with optional filters.",
        function=trade_history_tool.get_trade_history,
        requires_db=True,
        requires_user=True,
        category="trade_history",
        parameters=["db", "user_id", "symbol", "status_filter"],
    ),
    "trade_history.get_trade_details": ToolDefinition(
        name="trade_history.get_trade_details",
        description="Retrieve detailed information about a specific trade.",
        function=trade_history_tool.get_trade_details,
        requires_db=True,
        requires_user=True,
        category="trade_history",
        parameters=["db", "user_id", "trade_id"],
    ),
}


def get_tool(name: str) -> Optional[ToolDefinition]:
    """Lookup a tool by its fully qualified name."""
    return TOOLS.get(name)


def list_tools(category: Optional[str] = None) -> List[ToolDefinition]:
    """List all registered tools, optionally filtered by category."""
    tools = list(TOOLS.values())
    if category:
        tools = [t for t in tools if t.category == category]
    return tools


def get_tool_categories() -> List[str]:
    """Return unique sorted list of tool categories."""
    return sorted(set(t.category for t in TOOLS.values()))

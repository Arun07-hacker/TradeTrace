"""
TradeTrace Tool Layer.

Exposes agent-callable tools that wrap existing services.
Architecture: Agent → Tool → Service → Database / External API
"""

# ── Base ──
from app.tools.base import ToolResult, log_tool_execution

# ── Market Data ──
from app.tools.market_data_tool import get_market_data, get_historical_market_data

# ── Technical Analysis ──
from app.tools.technical_analysis_tool import calculate_indicators, analyze_trend

# ── News Search ──
from app.tools.news_search_tool import search_news, get_market_events

# ── Memory Search ──
from app.tools.memory_search_tool import search_similar_trades, get_previous_lessons

# ── Risk Calculator ──
from app.tools.risk_calculator_tool import calculate_position_size, calculate_risk_reward

# ── Portfolio ──
from app.tools.portfolio_tool import get_portfolio, get_open_positions

# ── Paper Trade ──
from app.tools.paper_trade_tool import create_paper_trade, close_paper_trade

# ── Alert ──
from app.tools.alert_tool import create_alert, get_alerts

# ── Trade History ──
from app.tools.trade_history_tool import get_trade_history, get_trade_details

# ── Trace ──
from app.tools.trace import ExecutionTrace, TraceEntry

# ── Registry ──
from app.tools.registry import TOOLS, get_tool, list_tools, get_tool_categories

__all__ = [
    # Base
    "ToolResult",
    "log_tool_execution",
    # Market Data
    "get_market_data",
    "get_historical_market_data",
    # Technical Analysis
    "calculate_indicators",
    "analyze_trend",
    # News Search
    "search_news",
    "get_market_events",
    # Memory Search
    "search_similar_trades",
    "get_previous_lessons",
    # Risk Calculator
    "calculate_position_size",
    "calculate_risk_reward",
    # Portfolio
    "get_portfolio",
    "get_open_positions",
    # Paper Trade
    "create_paper_trade",
    "close_paper_trade",
    # Alert
    "create_alert",
    "get_alerts",
    # Trade History
    "get_trade_history",
    "get_trade_details",
    # Trace
    "ExecutionTrace",
    "TraceEntry",
    # Registry
    "TOOLS",
    "get_tool",
    "list_tools",
    "get_tool_categories",
]

"""
Tests for the TradeTrace Tool Layer.

Tests every tool module using mock providers (no external API or DB required
for market_data, technical_analysis, news_search, and risk_calculator tools).
DB-dependent tools are tested with mocked AsyncSession.
"""
import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.tools.base import ToolResult
from app.tools.market_data_tool import get_market_data, get_historical_market_data
from app.tools.technical_analysis_tool import calculate_indicators, analyze_trend
from app.tools.news_search_tool import search_news, get_market_events
from app.tools.risk_calculator_tool import calculate_position_size, calculate_risk_reward
from app.tools.trace import ExecutionTrace, TraceEntry
from app.tools.registry import TOOLS, get_tool, list_tools, get_tool_categories


# ──────────────────────────────────────────────────────────────────
# Market Data Tool Tests
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_market_data_success():
    """get_market_data should return a ToolResult with success status and quote data."""
    result = await get_market_data("AAPL")
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert result.tool == "market_data.get_market_data"
    assert result.data is not None
    assert "symbol" in result.data
    assert result.data["symbol"] == "AAPL"
    assert "price" in result.data
    assert result.data["price"] > 0
    assert result.error is None


@pytest.mark.asyncio
async def test_get_historical_market_data_success():
    """get_historical_market_data should return OHLCV bars."""
    result = await get_historical_market_data("MSFT", timeframe="1d", limit=50)
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert result.tool == "market_data.get_historical_market_data"
    assert isinstance(result.data, list)
    assert len(result.data) == 50
    # Verify bar structure
    bar = result.data[0]
    assert "open" in bar
    assert "high" in bar
    assert "low" in bar
    assert "close" in bar
    assert "volume" in bar


@pytest.mark.asyncio
async def test_get_market_data_unlisted_symbol():
    """get_market_data should work for unlisted symbols using fallback."""
    result = await get_market_data("TCS")
    assert result.status == "success"
    assert result.data["symbol"] == "TCS"


# ──────────────────────────────────────────────────────────────────
# Technical Analysis Tool Tests
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_calculate_indicators_success():
    """calculate_indicators should return full technical analysis results."""
    result = await calculate_indicators("AAPL")
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert result.data is not None
    data = result.data
    assert "rsi" in data
    assert 0 <= data["rsi"] <= 100
    assert "macd" in data
    assert "trend" in data
    assert "atr" in data
    assert "support_resistance" in data


@pytest.mark.asyncio
async def test_analyze_trend_success():
    """analyze_trend should return trend summary with key levels."""
    result = await analyze_trend("TSLA")
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    data = result.data
    assert "trend" in data
    assert "trend_details" in data
    assert "rsi" in data
    assert "support_resistance" in data
    assert "volume_signal" in data


# ──────────────────────────────────────────────────────────────────
# News Search Tool Tests
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_news_success():
    """search_news should return articles for known symbols."""
    result = await search_news("NVDA", limit=3)
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert isinstance(result.data, list)
    assert len(result.data) > 0
    article = result.data[0]
    assert "title" in article
    assert "sentiment" in article
    assert "sentiment_score" in article


@pytest.mark.asyncio
async def test_get_market_events_success():
    """get_market_events should return upcoming events."""
    result = await get_market_events("AAPL")
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert isinstance(result.data, list)
    assert len(result.data) > 0
    event = result.data[0]
    assert "title" in event
    assert "event_type" in event
    assert "days_until" in event


@pytest.mark.asyncio
async def test_search_news_generic_symbol():
    """search_news should work for symbols without predefined news."""
    result = await search_news("UNKNOWN_TICKER")
    assert result.status == "success"
    assert len(result.data) > 0


# ──────────────────────────────────────────────────────────────────
# Risk Calculator Tool Tests
# ──────────────────────────────────────────────────────────────────

def test_calculate_position_size_success():
    """calculate_position_size should return valid risk metrics."""
    result = calculate_position_size(
        symbol="AAPL",
        direction="LONG",
        entry_price=220.0,
        stop_loss=215.0,
        target_price=235.0,
    )
    assert isinstance(result, ToolResult)
    assert result.status == "success"
    data = result.data
    assert data["symbol"] == "AAPL"
    assert data["direction"] == "LONG"
    assert data["position_size"] > 0
    assert data["risk_reward_ratio"] > 0
    assert data["is_valid"] is True


def test_calculate_position_size_invalid_geometry():
    """calculate_position_size should flag invalid stop/target geometry."""
    result = calculate_position_size(
        symbol="AAPL",
        direction="LONG",
        entry_price=220.0,
        stop_loss=225.0,  # Stop above entry for LONG = invalid
        target_price=235.0,
    )
    assert result.status == "success"
    data = result.data
    assert data["is_valid"] is False
    assert len(data["warnings"]) > 0


def test_calculate_risk_reward_success():
    """calculate_risk_reward should return ratio metrics."""
    result = calculate_risk_reward(
        entry_price=100.0,
        stop_loss=95.0,
        target_price=115.0,
        direction="LONG",
    )
    assert result.status == "success"
    data = result.data
    assert data["risk_per_share"] == 5.0
    assert data["reward_per_share"] == 15.0
    assert data["risk_reward_ratio"] == 3.0
    assert data["favorable"] is True


def test_calculate_risk_reward_short():
    """calculate_risk_reward should handle SHORT direction."""
    result = calculate_risk_reward(
        entry_price=200.0,
        stop_loss=210.0,
        target_price=180.0,
        direction="SHORT",
    )
    assert result.status == "success"
    data = result.data
    assert data["risk_per_share"] == 10.0
    assert data["reward_per_share"] == 20.0
    assert data["risk_reward_ratio"] == 2.0


def test_calculate_risk_reward_invalid_direction():
    """calculate_risk_reward should return error for invalid direction."""
    result = calculate_risk_reward(
        entry_price=100.0,
        stop_loss=95.0,
        target_price=115.0,
        direction="DIAGONAL",
    )
    assert result.status == "error"
    assert "Invalid direction" in result.error


# ──────────────────────────────────────────────────────────────────
# Memory Search Tool Tests (Mocked DB)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_similar_trades_mocked():
    """search_similar_trades should handle empty results gracefully."""
    from app.tools.memory_search_tool import search_similar_trades

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await search_similar_trades(
        db=mock_db,
        user_id=uuid.uuid4(),
        thesis="Breakout with volume",
    )
    assert isinstance(result, ToolResult)
    # Should succeed even with empty results
    assert result.status == "success"
    assert result.data == []


@pytest.mark.asyncio
async def test_get_previous_lessons_mocked():
    """get_previous_lessons should handle DB errors gracefully."""
    from app.tools.memory_search_tool import get_previous_lessons

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB unavailable")

    result = await get_previous_lessons(
        db=mock_db,
        user_id=uuid.uuid4(),
        thesis="Breakout with volume",
    )
    assert isinstance(result, ToolResult)
    assert result.status == "error"
    assert "DB unavailable" in result.error


# ──────────────────────────────────────────────────────────────────
# Portfolio Tool Tests (Mocked DB)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_portfolio_error_handling():
    """get_portfolio should return error ToolResult when DB fails."""
    from app.tools.portfolio_tool import get_portfolio

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("Connection refused")

    result = await get_portfolio(db=mock_db, user_id=uuid.uuid4())
    assert isinstance(result, ToolResult)
    assert result.status == "error"
    assert "Connection refused" in result.error


@pytest.mark.asyncio
async def test_get_open_positions_error_handling():
    """get_open_positions should return error ToolResult when DB fails."""
    from app.tools.portfolio_tool import get_open_positions

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("Connection refused")

    result = await get_open_positions(db=mock_db, user_id=uuid.uuid4())
    assert isinstance(result, ToolResult)
    assert result.status == "error"
    assert "Connection refused" in result.error


# ──────────────────────────────────────────────────────────────────
# Paper Trade Tool Tests (Mocked DB)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_paper_trade_error_handling():
    """create_paper_trade should return error ToolResult when DB fails."""
    from app.tools.paper_trade_tool import create_paper_trade

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB error")

    result = await create_paper_trade(
        db=mock_db,
        user_id=uuid.uuid4(),
        symbol="AAPL",
        direction="LONG",
        entry_price=220.0,
        stop_loss=215.0,
        target=235.0,
        quantity=10,
        thesis="Breakout with strong volume",
    )
    assert isinstance(result, ToolResult)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_close_paper_trade_error_handling():
    """close_paper_trade should return error ToolResult when trade not found."""
    from app.tools.paper_trade_tool import close_paper_trade

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await close_paper_trade(
        db=mock_db,
        user_id=uuid.uuid4(),
        trade_id=uuid.uuid4(),
    )
    assert isinstance(result, ToolResult)
    assert result.status == "error"


# ──────────────────────────────────────────────────────────────────
# Alert Tool Tests (Mocked DB)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_alerts_error_handling():
    """get_alerts should return error ToolResult when DB fails."""
    from app.tools.alert_tool import get_alerts

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB error")

    result = await get_alerts(db=mock_db, user_id=uuid.uuid4())
    assert isinstance(result, ToolResult)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_create_alert_error_handling():
    """create_alert should return error ToolResult when DB fails."""
    from app.tools.alert_tool import create_alert

    mock_db = AsyncMock()
    mock_db.commit.side_effect = Exception("DB error")

    result = await create_alert(
        db=mock_db,
        user_id=uuid.uuid4(),
        symbol="AAPL",
        alert_type="TEST",
        title="Test Alert",
        message="Test message",
    )
    assert isinstance(result, ToolResult)
    assert result.status == "error"


# ──────────────────────────────────────────────────────────────────
# Trade History Tool Tests (Mocked DB)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_trade_history_error_handling():
    """get_trade_history should return error ToolResult when DB fails."""
    from app.tools.trade_history_tool import get_trade_history

    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB error")

    result = await get_trade_history(db=mock_db, user_id=uuid.uuid4())
    assert isinstance(result, ToolResult)
    assert result.status == "error"


@pytest.mark.asyncio
async def test_get_trade_details_error_handling():
    """get_trade_details should return error for nonexistent trade."""
    from app.tools.trade_history_tool import get_trade_details

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await get_trade_details(
        db=mock_db,
        user_id=uuid.uuid4(),
        trade_id=uuid.uuid4(),
    )
    assert isinstance(result, ToolResult)
    assert result.status == "error"
    assert "not found" in result.error


# ──────────────────────────────────────────────────────────────────
# Execution Trace Tests
# ──────────────────────────────────────────────────────────────────

def test_execution_trace_lifecycle():
    """ExecutionTrace should track start, complete, and fail entries."""
    trace = ExecutionTrace()
    trace.start("tool", "market_data")
    trace.complete("tool", "market_data", "100 bars retrieved")

    trace.start("tool", "news_search")
    trace.fail("tool", "news_search", "Provider unavailable")

    trace.skip("tool", "memory_search", "requires database")

    entries = trace.to_list()
    assert len(entries) == 3

    assert entries[0]["name"] == "market_data"
    assert entries[0]["status"] == "completed"
    assert entries[0]["result_summary"] == "100 bars retrieved"

    assert entries[1]["name"] == "news_search"
    assert entries[1]["status"] == "error"
    assert entries[1]["error"] == "Provider unavailable"

    assert entries[2]["name"] == "memory_search"
    assert entries[2]["status"] == "skipped"


def test_execution_trace_print_summary(capsys):
    """ExecutionTrace.print_summary should produce formatted output."""
    trace = ExecutionTrace()
    trace.start("tool", "market_data")
    trace.complete("tool", "market_data", "OK")
    trace.print_summary()
    captured = capsys.readouterr()
    assert "EXECUTION TRACE" in captured.out
    assert "market_data" in captured.out
    assert "[OK]" in captured.out


# ──────────────────────────────────────────────────────────────────
# Tool Registry Tests
# ──────────────────────────────────────────────────────────────────

def test_registry_has_all_tools():
    """Registry should contain all 18 expected tool functions."""
    expected_tools = [
        "market_data.get_market_data",
        "market_data.get_historical_market_data",
        "technical_analysis.calculate_indicators",
        "technical_analysis.analyze_trend",
        "news_search.search_news",
        "news_search.get_market_events",
        "memory_search.search_similar_trades",
        "memory_search.get_previous_lessons",
        "risk_calculator.calculate_position_size",
        "risk_calculator.calculate_risk_reward",
        "portfolio.get_portfolio",
        "portfolio.get_open_positions",
        "paper_trade.create_paper_trade",
        "paper_trade.close_paper_trade",
        "alert.create_alert",
        "alert.get_alerts",
        "trade_history.get_trade_history",
        "trade_history.get_trade_details",
    ]
    for name in expected_tools:
        assert name in TOOLS, f"Tool '{name}' missing from registry"


def test_get_tool_found():
    """get_tool should return ToolDefinition for valid names."""
    tool = get_tool("market_data.get_market_data")
    assert tool is not None
    assert tool.name == "market_data.get_market_data"
    assert callable(tool.function)
    assert tool.requires_db is False


def test_get_tool_not_found():
    """get_tool should return None for unknown tool names."""
    assert get_tool("nonexistent.tool") is None


def test_list_tools_by_category():
    """list_tools with category filter should return only matching tools."""
    market_tools = list_tools(category="market_data")
    assert len(market_tools) == 2
    assert all(t.category == "market_data" for t in market_tools)


def test_get_tool_categories():
    """get_tool_categories should return all unique categories."""
    categories = get_tool_categories()
    expected = ["alert", "market_data", "memory_search", "news_search",
                "paper_trade", "portfolio", "risk_calculator",
                "technical_analysis", "trade_history"]
    assert categories == expected


def test_db_required_tools_are_marked():
    """All DB-dependent tools should be marked with requires_db=True."""
    db_tool_names = [
        "memory_search.search_similar_trades",
        "memory_search.get_previous_lessons",
        "portfolio.get_portfolio",
        "portfolio.get_open_positions",
        "paper_trade.create_paper_trade",
        "paper_trade.close_paper_trade",
        "alert.create_alert",
        "alert.get_alerts",
        "trade_history.get_trade_history",
        "trade_history.get_trade_details",
    ]
    for name in db_tool_names:
        tool = get_tool(name)
        assert tool is not None, f"Tool '{name}' not found"
        assert tool.requires_db is True, f"Tool '{name}' should require DB"
        assert tool.requires_user is True, f"Tool '{name}' should require user"

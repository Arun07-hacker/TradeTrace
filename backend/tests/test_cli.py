"""
Tests for the TradeTrace Terminal CLI.

Tests argument parsing, user input flow, and analysis execution
using mock providers (no external API or DB required).
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from io import StringIO

from app.cli import parse_args, run_analysis


# ──────────────────────────────────────────────────────────────────
# Argument Parsing Tests
# ──────────────────────────────────────────────────────────────────

def test_parse_args_empty():
    """parse_args with no arguments should set all to None."""
    with patch("sys.argv", ["cli"]):
        args = parse_args()
        assert args.symbol is None
        assert args.direction is None
        assert args.entry is None
        assert args.stop is None
        assert args.target is None
        assert args.thesis is None


def test_parse_args_full():
    """parse_args with all arguments should populate correctly."""
    with patch("sys.argv", [
        "cli",
        "--symbol", "AAPL",
        "--direction", "LONG",
        "--entry", "220.0",
        "--stop", "215.0",
        "--target", "235.0",
        "--thesis", "Breakout above resistance with volume confirmation",
    ]):
        args = parse_args()
        assert args.symbol == "AAPL"
        assert args.direction == "LONG"
        assert args.entry == 220.0
        assert args.stop == 215.0
        assert args.target == 235.0
        assert args.thesis == "Breakout above resistance with volume confirmation"


def test_parse_args_short_flags():
    """parse_args should accept short flag variants."""
    with patch("sys.argv", [
        "cli",
        "-s", "TSLA",
        "-d", "SHORT",
        "-e", "250.0",
        "-t", "230.0",
    ]):
        args = parse_args()
        assert args.symbol == "TSLA"
        assert args.direction == "SHORT"
        assert args.entry == 250.0
        assert args.target == 230.0


# ──────────────────────────────────────────────────────────────────
# Analysis Execution Tests (with Mock Providers)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_analysis_completes(capsys):
    """run_analysis should complete without errors using mock providers."""
    params = {
        "symbol": "AAPL",
        "direction": "LONG",
        "entry_price": 220.0,
        "stop_loss": 215.0,
        "target_price": 235.0,
        "thesis": "Breakout above resistance with volume confirmation and momentum",
    }
    await run_analysis(params)

    captured = capsys.readouterr()
    # Verify key sections appear in output
    assert "TRADETRACE TERMINAL ANALYSIS" in captured.out
    assert "TOOL → MARKET DATA" in captured.out
    assert "TOOL → TECHNICAL ANALYSIS" in captured.out
    assert "TOOL → NEWS SEARCH" in captured.out
    assert "TOOL → RISK CALCULATOR" in captured.out
    assert "AGENT → RESEARCH" in captured.out
    assert "AGENT → DEVIL'S ADVOCATE" in captured.out
    assert "AGENT → DECISION" in captured.out
    assert "EXECUTION TRACE" in captured.out
    assert "TRADETRACE ANALYSIS COMPLETE" in captured.out


@pytest.mark.asyncio
async def test_run_analysis_shows_risk_metrics(capsys):
    """run_analysis should display risk calculation results."""
    params = {
        "symbol": "NVDA",
        "direction": "LONG",
        "entry_price": 125.0,
        "stop_loss": 120.0,
        "target_price": 140.0,
        "thesis": "GPU demand acceleration with data center buildout",
    }
    await run_analysis(params)

    captured = capsys.readouterr()
    assert "Position Size:" in captured.out
    assert "Risk/Reward:" in captured.out
    assert "Risk Level:" in captured.out


@pytest.mark.asyncio
async def test_run_analysis_unknown_symbol(capsys):
    """run_analysis should work for unlisted symbols using fallback providers."""
    params = {
        "symbol": "TCS",
        "direction": "LONG",
        "entry_price": 3800.0,
        "stop_loss": 3750.0,
        "target_price": 3900.0,
        "thesis": "Breakout with increasing volume above key resistance levels",
    }
    await run_analysis(params)

    captured = capsys.readouterr()
    assert "TRADETRACE ANALYSIS COMPLETE" in captured.out
    assert "DECISION:" in captured.out


@pytest.mark.asyncio
async def test_run_analysis_short_direction(capsys):
    """run_analysis should work correctly with SHORT direction."""
    params = {
        "symbol": "TSLA",
        "direction": "SHORT",
        "entry_price": 250.0,
        "stop_loss": 260.0,
        "target_price": 230.0,
        "thesis": "Distribution pattern with declining volume and bearish divergence",
    }
    await run_analysis(params)

    captured = capsys.readouterr()
    assert "TRADETRACE ANALYSIS COMPLETE" in captured.out
    assert "SHORT" in captured.out

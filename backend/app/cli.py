"""
TradeTrace Terminal CLI.

Run the full multi-agent analysis pipeline from the command line.

Usage:
    python -m app.cli
    python -m app.cli --symbol AAPL
    python -m app.cli --symbol AAPL --direction LONG --entry 220 --stop 215 --target 235 --thesis "Breakout"

Works offline with mock providers. Database-dependent tools (memory, portfolio, alerts)
are gracefully skipped when no DB is available.
"""
import argparse
import asyncio
import sys
import os
import json
import warnings

# Suppress NumPy/dependency RuntimeWarnings on Windows
warnings.filterwarnings("ignore")

from app.tools.base import format_log
from app.tools.market_data_tool import get_market_data, get_historical_market_data
from app.tools.technical_analysis_tool import calculate_indicators, analyze_trend
from app.tools.news_search_tool import search_news, get_market_events
from app.tools.risk_calculator_tool import calculate_position_size, calculate_risk_reward
from app.tools.trace import ExecutionTrace

from app.schemas.market import OHLCVBar
from app.schemas.technical import TechnicalAnalysisResult
from app.schemas.news import NewsArticleItem, MarketEventItem
from app.schemas.risk import RiskCalculationResponse
from app.schemas.memory import MemorySearchResultItem

from app.analysis.engine import TechnicalAnalysisEngine
from app.agents.research_agent import ResearchAgent
from app.agents.devil_advocate_agent import DevilsAdvocateAgent
from app.agents.decision_agent import DecisionAgent


BANNER = r"""
========================================================
                                                        
   TRADETRACE                                           
                                                        
   AI Trading Research & Learning Assistant              
   Research -> Challenge -> Decide -> Monitor -> Learn   
                                                        
========================================================
"""



def print_section(title: str, icon: str = "-") -> None:
    """Print a formatted section header."""
    print(f"\n{icon * 3} {title}")
    print("-" * 50)


def print_result(label: str, success: bool = True) -> None:
    """Print a result line with status icon."""
    icon = "[OK]" if success else "[!!]"
    print(f"  {icon} {label}")


def get_user_input(args: argparse.Namespace) -> dict:
    """Get analysis parameters from args or interactive prompt."""
    params = {}

    # Symbol
    if args.symbol:
        params["symbol"] = args.symbol.upper().strip()
    else:
        params["symbol"] = input("\n  Symbol: ").upper().strip()
        if not params["symbol"]:
            params["symbol"] = "AAPL"
            print(f"  → Using default: {params['symbol']}")

    # Direction
    if args.direction:
        params["direction"] = args.direction.upper().strip()
    else:
        direction = input("  Direction (LONG/SHORT): ").upper().strip()
        params["direction"] = direction if direction in ("LONG", "SHORT") else "LONG"

    # Entry Price
    if args.entry:
        params["entry_price"] = args.entry
    else:
        try:
            params["entry_price"] = float(input("  Entry Price: $"))
        except (ValueError, EOFError):
            params["entry_price"] = 100.0
            print(f"  → Using default: ${params['entry_price']}")

    # Stop Loss
    if args.stop:
        params["stop_loss"] = args.stop
    else:
        try:
            params["stop_loss"] = float(input("  Stop Loss: $"))
        except (ValueError, EOFError):
            params["stop_loss"] = params["entry_price"] * 0.97
            print(f"  → Using default: ${params['stop_loss']:.2f}")

    # Target
    if args.target:
        params["target_price"] = args.target
    else:
        try:
            params["target_price"] = float(input("  Target: $"))
        except (ValueError, EOFError):
            params["target_price"] = params["entry_price"] * 1.05
            print(f"  → Using default: ${params['target_price']:.2f}")

    # Thesis
    if args.thesis:
        params["thesis"] = args.thesis
    else:
        thesis = input("  Trading Thesis: ")
        params["thesis"] = thesis if len(thesis) >= 10 else "Technical breakout with volume confirmation above key resistance."
        if len(thesis) < 10:
            print(f"  → Using default thesis")

    return params


async def run_analysis(params: dict) -> None:
    """Execute the full analysis pipeline using tools and agents."""
    sym = params["symbol"]
    direction = params["direction"]
    entry = params["entry_price"]
    stop = params["stop_loss"]
    target = params["target_price"]
    thesis = params["thesis"]

    trace = ExecutionTrace()

    print("\n" + "=" * 55)
    print("  TRADETRACE TERMINAL ANALYSIS")
    print("=" * 55)
    print(f"\n  Symbol:    {sym}")
    print(f"  Direction: {direction}")
    print(f"  Entry:     ${entry:.2f}")
    print(f"  Stop:      ${stop:.2f}")
    print(f"  Target:    ${target:.2f}")
    print(f"  Thesis:    {thesis[:80]}...")

    # ── ORCHESTRATOR ──
    print_section("ORCHESTRATOR")
    print("  Creating analysis workflow...")

    # ──────────────────────────────────────────────
    # TOOL → Market Data
    # ──────────────────────────────────────────────
    print_section("TOOL → MARKET DATA")
    trace.start("tool", "market_data")
    market_result = await get_historical_market_data(symbol=sym, timeframe="1d", limit=100)
    if market_result.status == "success":
        bars_raw = market_result.data
        bars = [OHLCVBar(**b) if isinstance(b, dict) else b for b in bars_raw]
        print_result(f"Market data retrieved ({len(bars)} bars)")
        trace.complete("tool", "market_data", f"{len(bars)} bars")
    else:
        print_result(f"Market data error: {market_result.error}", success=False)
        trace.fail("tool", "market_data", market_result.error or "Unknown")
        bars = []

    # Also get latest quote
    quote_result = await get_market_data(symbol=sym)
    if quote_result.status == "success":
        quote = quote_result.data
        print_result(f"Latest quote: ${quote.get('price', 'N/A')}")

    # ──────────────────────────────────────────────
    # TOOL → Technical Analysis
    # ──────────────────────────────────────────────
    print_section("TOOL → TECHNICAL ANALYSIS")
    trace.start("tool", "technical_analysis")
    tech_result = await calculate_indicators(symbol=sym, timeframe="1d", limit=100)
    if tech_result.status == "success":
        technicals = TechnicalAnalysisResult(**tech_result.data)
        print_result(f"RSI: {technicals.rsi:.1f}")
        print_result(f"EMA 12/26: {technicals.ema_12:.2f} / {technicals.ema_26:.2f}")
        print_result(f"MACD: {technicals.macd.macd:.2f} (Signal: {technicals.macd.signal:.2f})")
        print_result(f"ATR: {technicals.atr:.2f}")
        print_result(f"Trend: {technicals.trend} (Strength: {technicals.trend_details.strength:.2f})")
        print_result(f"Volume: {technicals.volume_signal}")
        trace.complete("tool", "technical_analysis", f"RSI={technicals.rsi:.1f}, Trend={technicals.trend}")
    else:
        print_result(f"Technical analysis error: {tech_result.error}", success=False)
        trace.fail("tool", "technical_analysis", tech_result.error or "Unknown")
        if bars:
            technicals = TechnicalAnalysisEngine.analyze(sym, bars, is_demo=True)
        else:
            print("\n  ✗ Cannot proceed without market data or technical analysis.")
            return

    # ──────────────────────────────────────────────
    # TOOL → News Search
    # ──────────────────────────────────────────────
    print_section("TOOL → NEWS SEARCH")
    trace.start("tool", "news_search")
    news_result = await search_news(symbol=sym, limit=5)
    if news_result.status == "success":
        news_articles = [NewsArticleItem(**a) if isinstance(a, dict) else a for a in news_result.data]
        for article in news_articles[:3]:
            sentiment_icon = "↑" if article.sentiment_score > 0 else ("↓" if article.sentiment_score < 0 else "→")
            print_result(f"{sentiment_icon} {article.title[:60]}...")
        trace.complete("tool", "news_search", f"{len(news_articles)} articles")
    else:
        news_articles = []
        print_result("No news available", success=False)
        trace.fail("tool", "news_search", news_result.error or "No news")

    # ──────────────────────────────────────────────
    # TOOL → Market Events
    # ──────────────────────────────────────────────
    print_section("TOOL → MARKET EVENTS")
    trace.start("tool", "market_events")
    events_result = await get_market_events(symbol=sym)
    if events_result.status == "success":
        events = [MarketEventItem(**e) if isinstance(e, dict) else e for e in events_result.data]
        for ev in events[:3]:
            print_result(f"{ev.event_type}: {ev.title} (in {ev.days_until}d)")
        trace.complete("tool", "market_events", f"{len(events)} events")
    else:
        events = []
        print_result("No upcoming events", success=False)
        trace.fail("tool", "market_events", events_result.error or "No events")

    # ──────────────────────────────────────────────
    # TOOL → Trading Memory (SKIPPED in CLI mode)
    # ──────────────────────────────────────────────
    print_section("TOOL → TRADING MEMORY")
    trace.skip("tool", "memory_search", "requires database")
    print("  ○ Skipped — requires database connection")
    print("  ○ In production, this searches previous similar trades and lessons")
    memory_items = []

    # ──────────────────────────────────────────────
    # TOOL → Risk Calculator
    # ──────────────────────────────────────────────
    print_section("TOOL → RISK CALCULATOR")
    trace.start("tool", "risk_calculator")
    risk_result = calculate_position_size(
        symbol=sym,
        direction=direction,
        entry_price=entry,
        stop_loss=stop,
        target_price=target,
    )
    if risk_result.status == "success":
        risk_calc = RiskCalculationResponse(**risk_result.data)
        print_result(f"Position Size: {risk_calc.position_size} shares")
        print_result(f"Risk/Reward: 1:{risk_calc.risk_reward_ratio}")
        print_result(f"Risk Amount: ${risk_calc.risk_amount:,.2f}")
        print_result(f"Position Value: ${risk_calc.position_value:,.2f}")
        print_result(f"Portfolio Exposure: {risk_calc.portfolio_exposure_pct:.1f}%")
        print_result(f"Risk Level: {risk_calc.risk_level.upper()}")
        if risk_calc.warnings:
            for w in risk_calc.warnings:
                print_result(f"⚠ {w}", success=False)
        trace.complete("tool", "risk_calculator", f"R:R=1:{risk_calc.risk_reward_ratio}")
    else:
        print_result(f"Risk calculation error: {risk_result.error}", success=False)
        trace.fail("tool", "risk_calculator", risk_result.error or "Unknown")
        print("\n  ✗ Cannot proceed without risk calculation.")
        return

    # ──────────────────────────────────────────────
    # AGENT → Research Agent
    # ──────────────────────────────────────────────
    print_section("AGENT → RESEARCH")
    print("  Research Agent analyzing evidence...")
    trace.start("agent", "research")
    research_agent = ResearchAgent()
    research_output = await research_agent.analyze(
        symbol=sym,
        direction=direction,
        thesis=thesis,
        technicals=technicals,
        articles=news_articles,
        events=events,
    )
    print_result(f"Technical: {research_output.technical_evaluation[:70]}...")
    print_result(f"Catalyst: {research_output.catalyst_evaluation[:70]}...")
    print_result(f"Alignment Score: {research_output.alignment_score:.2f}")
    print(f"  Supporting: {', '.join(research_output.supporting_points[:2])}")
    print(f"  Risks:      {', '.join(research_output.risk_points[:2])}")
    trace.complete("agent", "research",
                   f"Alignment={research_output.alignment_score:.2f}",
                   tools_used=["market_data", "technical_analysis", "news_search"])

    # ──────────────────────────────────────────────
    # AGENT → Devil's Advocate
    # ──────────────────────────────────────────────
    print_section("AGENT → DEVIL'S ADVOCATE")
    print("  Challenging trader thesis...")
    trace.start("agent", "devils_advocate")
    devil_advocate = DevilsAdvocateAgent()
    devil_output = await devil_advocate.challenge(
        symbol=sym,
        direction=direction,
        thesis=thesis,
        research=research_output,
        technicals=technicals,
        memory_items=memory_items,
    )
    print_result(f"Counter arguments: {len(devil_output.counter_arguments)}")
    for ca in devil_output.counter_arguments[:2]:
        print(f"    → {ca[:70]}...")
    print_result(f"Bias Warning: {devil_output.confirmation_bias_warning[:70]}...")
    print_result(f"Skepticism Score: {devil_output.skepticism_score:.2f}")
    trace.complete("agent", "devils_advocate",
                   f"Skepticism={devil_output.skepticism_score:.2f}",
                   tools_used=["technical_analysis", "news_search", "memory_search"])

    # ──────────────────────────────────────────────
    # AGENT → Decision Agent
    # ──────────────────────────────────────────────
    print_section("AGENT → DECISION")
    print("  Combining evidence...")
    trace.start("agent", "decision")
    decision_agent = DecisionAgent()
    decision_output = await decision_agent.decide(
        symbol=sym,
        direction=direction,
        thesis=thesis,
        research=research_output,
        devils_advocate=devil_output,
        risk=risk_calc,
    )
    trace.complete("agent", "decision",
                   f"Action={decision_output.action}")

    # ──────────────────────────────────────────────
    # DECISION OUTPUT
    # ──────────────────────────────────────────────
    print("\n" + "=" * 55)
    action_colors = {
        "PROCEED_WITH_CAUTION": "✓",
        "WAIT_FOR_CONFIRMATION": "◐",
        "REVISE_PARAMETERS": "⚠",
        "REJECT": "✗",
    }
    icon = action_colors.get(decision_output.action, "?")
    print(f"\n  {icon} DECISION: {decision_output.action}")
    print(f"\n  Thesis Strength: {decision_output.thesis_strength:.2f}")
    print(f"  Confidence:      {decision_output.confidence:.2f}")
    print(f"\n  Summary:")
    # Wrap summary text
    summary = decision_output.summary
    while summary:
        print(f"    {summary[:70]}")
        summary = summary[70:]

    if decision_output.suggested_modifications:
        print(f"\n  Suggested Modifications:")
        for mod in decision_output.suggested_modifications[:3]:
            print(f"    → {mod[:70]}")

    if decision_output.memory_warnings:
        print(f"\n  Memory Warnings:")
        for mw in decision_output.memory_warnings[:3]:
            print(f"    ⚠ {mw[:70]}")

    # ──────────────────────────────────────────────
    # EXECUTION TRACE
    # ──────────────────────────────────────────────
    trace.print_summary()

    print("=" * 55)
    print("  TRADETRACE ANALYSIS COMPLETE")
    print("=" * 55 + "\n")


async def run_direct_tool(tool_query: str, symbol: str, direction: str, entry: float, stop: float, target: float, thesis: str) -> None:
    """Execute a specific tool or category of tools directly from CLI."""
    from app.tools.registry import TOOLS, list_tools

    symbol = (symbol or "AAPL").upper()
    direction = (direction or "LONG").upper()
    entry = entry or 100.0
    stop = stop or 95.0
    target = target or 110.0

    matching_tools = [
        name for name in TOOLS
        if name == tool_query or name.startswith(f"{tool_query}.") or TOOLS[name].category == tool_query
    ]

    if not matching_tools:
        print(f"\n  [!!] Tool or category '{tool_query}' not found.")
        print("  Use --list-tools to see all available tools.")
        return

    print(f"\n========================================================")
    print(f"  TRADETRACE DIRECT TOOL EXECUTION")
    print(f"  Target: {tool_query} | Symbol: {symbol}")
    print(f"========================================================\n")

    for tool_name in matching_tools:
        tool_def = TOOLS[tool_name]
        print(f"--> Executing tool: [{tool_name}]")
        print(f"    Description: {tool_def.description}")

        if tool_def.requires_db:
            print("    [!!] Skipped: Tool requires an active database connection.")
            print()
            continue

        try:
            # Build argument dictionary based on tool parameters
            kwargs = {}
            if "symbol" in tool_def.parameters:
                kwargs["symbol"] = symbol
            if "timeframe" in tool_def.parameters:
                kwargs["timeframe"] = "1d"
            if "limit" in tool_def.parameters:
                kwargs["limit"] = 10
            if "direction" in tool_def.parameters:
                kwargs["direction"] = direction
            if "entry_price" in tool_def.parameters:
                kwargs["entry_price"] = entry
            if "stop_loss" in tool_def.parameters:
                kwargs["stop_loss"] = stop
            if "target_price" in tool_def.parameters:
                kwargs["target_price"] = target

            # Execute tool function (sync or async)
            if asyncio.iscoroutinefunction(tool_def.function):
                result = await tool_def.function(**kwargs)
            else:
                result = tool_def.function(**kwargs)

            # Format result
            status = getattr(result, "status", "success")
            data = getattr(result, "data", result)
            error = getattr(result, "error", None)

            if status == "success":
                print("    [OK] Result:")
                if isinstance(data, (dict, list)):
                    print(json.dumps(data, indent=6, default=str))
                else:
                    print(f"      {data}")
            else:
                print(f"    [!!] Error: {error}")

        except Exception as e:
            print(f"    [!!] Execution Exception: {e}")

        print()


def show_registered_tools() -> None:
    """Print all registered tools in a structured table."""
    from app.tools.registry import TOOLS, get_tool_categories

    print(BANNER)
    print("========================================================")
    print("  TRADETRACE AGENT TOOL REGISTRY")
    print("========================================================\n")

    categories = get_tool_categories()
    for cat in categories:
        print(f"  Category: [{cat.upper()}]")
        cat_tools = [t for t in TOOLS.values() if t.category == cat]
        for t in cat_tools:
            db_flag = " (DB Required)" if t.requires_db else ""
            print(f"    - {t.name:<40} {db_flag}")
            print(f"      Description: {t.description}")
            print(f"      Parameters:  {', '.join(t.parameters)}")
        print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="tradetrace",
        description="TradeTrace — AI Trading Research & Learning Assistant CLI",
    )
    parser.add_argument("--symbol", "-s", type=str, help="Ticker symbol (e.g. AAPL, TCS, TSLA)")
    parser.add_argument("--direction", "-d", type=str, choices=["LONG", "SHORT", "long", "short"],
                        help="Trade direction")
    parser.add_argument("--entry", "-e", type=float, help="Entry price")
    parser.add_argument("--stop", type=float, help="Stop loss price")
    parser.add_argument("--target", "-t", type=float, help="Target price")
    parser.add_argument("--thesis", type=str, help="Trading thesis (min 10 chars)")
    parser.add_argument("--tool", type=str, help="Execute a specific tool or tool category directly (e.g. market_data, technical_analysis, risk_calculator)")
    parser.add_argument("--list-tools", action="store_true", help="List all registered agent tools")
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()

    if args.list_tools:
        show_registered_tools()
        return

    if args.tool:
        asyncio.run(run_direct_tool(
            tool_query=args.tool,
            symbol=args.symbol,
            direction=args.direction,
            entry=args.entry,
            stop=args.stop,
            target=args.target,
            thesis=args.thesis,
        ))
        return

    print(BANNER)
    params = get_user_input(args)
    asyncio.run(run_analysis(params))


if __name__ == "__main__":
    main()

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import (
    TradeAnalysisRequest,
    TradeAnalysisResponse,
)
from app.schemas.risk import RiskCalculationRequest
from app.schemas.market import OHLCVBar
from app.schemas.technical import TechnicalAnalysisResult
from app.schemas.news import NewsArticleItem, MarketEventItem
from app.schemas.memory import MemorySearchResultItem
from app.analysis.engine import TechnicalAnalysisEngine
from app.agents.research_agent import ResearchAgent
from app.agents.devil_advocate_agent import DevilsAdvocateAgent
from app.agents.decision_agent import DecisionAgent

from app.tools.base import ToolResult, format_log
from app.tools.market_data_tool import get_historical_market_data
from app.tools.technical_analysis_tool import calculate_indicators
from app.tools.news_search_tool import search_news, get_market_events
from app.tools.memory_search_tool import search_similar_trades, get_previous_lessons
from app.tools.risk_calculator_tool import calculate_position_size
from app.tools.trace import ExecutionTrace


class AgentOrchestrator:
    """
    Multi-Agent Pipeline Orchestrator:
    Coordinates deterministic technical analysis, news sentiment,
    pgvector memory retrieval, quantitative risk calculations,
    and LLM agent deliberation.

    Routes all data fetching through the Tool layer:
    Agent → Tool → Service → Database / External API
    """

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.devil_advocate = DevilsAdvocateAgent()
        self.decision_agent = DecisionAgent()

    async def analyze_trade(
        self,
        req: TradeAnalysisRequest,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> TradeAnalysisResponse:
        sym = req.symbol.upper().strip()
        trace = ExecutionTrace()

        # ──────────────────────────────────────────────
        # 1. TOOL → Market Data (historical bars)
        # ──────────────────────────────────────────────
        trace.start("tool", "market_data")
        market_result = await get_historical_market_data(
            symbol=sym, timeframe=req.timeframe, limit=100,
        )
        if market_result.status == "success":
            bars_raw = market_result.data
            bars = [OHLCVBar(**b) if isinstance(b, dict) else b for b in bars_raw]
            trace.complete("tool", "market_data", f"{len(bars)} bars retrieved")
        else:
            trace.fail("tool", "market_data", market_result.error or "Unknown error")
            bars = []

        # ──────────────────────────────────────────────
        # 2. TOOL → Technical Analysis
        # ──────────────────────────────────────────────
        trace.start("tool", "technical_analysis")
        tech_result = await calculate_indicators(
            symbol=sym, timeframe=req.timeframe, limit=100,
        )
        if tech_result.status == "success":
            technicals = TechnicalAnalysisResult(**tech_result.data)
            trace.complete(
                "tool", "technical_analysis",
                f"RSI={technicals.rsi:.1f}, Trend={technicals.trend}",
            )
        else:
            trace.fail("tool", "technical_analysis", tech_result.error or "Unknown error")
            # Fallback: compute directly from bars if tool result had error but bars exist
            if bars:
                technicals = TechnicalAnalysisEngine.analyze(sym, bars, is_demo=True)
            else:
                raise RuntimeError("Cannot analyze: no market data or technical analysis available.")

        # ──────────────────────────────────────────────
        # 3. TOOL → News Search
        # ──────────────────────────────────────────────
        trace.start("tool", "news_search")
        news_result = await search_news(symbol=sym, limit=5)
        if news_result.status == "success":
            news_articles = [NewsArticleItem(**a) if isinstance(a, dict) else a for a in news_result.data]
            trace.complete("tool", "news_search", f"{len(news_articles)} articles")
        else:
            news_articles = []
            trace.fail("tool", "news_search", news_result.error or "No news")

        # ──────────────────────────────────────────────
        # 4. TOOL → Market Events
        # ──────────────────────────────────────────────
        trace.start("tool", "market_events")
        events_result = await get_market_events(symbol=sym)
        if events_result.status == "success":
            events = [MarketEventItem(**e) if isinstance(e, dict) else e for e in events_result.data]
            trace.complete("tool", "market_events", f"{len(events)} events")
        else:
            events = []
            trace.fail("tool", "market_events", events_result.error or "No events")

        # ──────────────────────────────────────────────
        # 5. TOOL → Risk Calculator
        # ──────────────────────────────────────────────
        trace.start("tool", "risk_calculator")
        risk_result = calculate_position_size(
            symbol=sym,
            direction=req.direction,
            entry_price=req.entry_price,
            stop_loss=req.stop_loss,
            target_price=req.target_price,
            portfolio_equity=req.portfolio_equity,
            risk_per_trade_pct=req.risk_per_trade_pct,
        )
        from app.schemas.risk import RiskCalculationResponse
        if risk_result.status == "success":
            risk_calc = RiskCalculationResponse(**risk_result.data)
            trace.complete(
                "tool", "risk_calculator",
                f"R:R=1:{risk_calc.risk_reward_ratio}, Size={risk_calc.position_size}",
            )
        else:
            trace.fail("tool", "risk_calculator", risk_result.error or "Unknown error")
            raise RuntimeError(f"Risk calculation failed: {risk_result.error}")

        # ──────────────────────────────────────────────
        # 6. TOOL → Memory Search (requires DB)
        # ──────────────────────────────────────────────
        memory_items = []
        try:
            trace.start("tool", "memory_search_lessons")
            lessons_result = await get_previous_lessons(
                db=db, user_id=user_id, thesis=req.thesis, top_k=3,
            )
            if lessons_result.status == "success" and lessons_result.data:
                for item_data in lessons_result.data:
                    memory_items.append(MemorySearchResultItem(**item_data))
                trace.complete("tool", "memory_search_lessons", f"{len(lessons_result.data)} lessons")
            else:
                trace.complete("tool", "memory_search_lessons", "No lessons found")

            trace.start("tool", "memory_search_trades")
            trades_result = await search_similar_trades(
                db=db, user_id=user_id, thesis=req.thesis, symbol=sym, top_k=3,
            )
            if trades_result.status == "success" and trades_result.data:
                for item_data in trades_result.data:
                    memory_items.append(MemorySearchResultItem(**item_data))
                trace.complete("tool", "memory_search_trades", f"{len(trades_result.data)} memories")
            else:
                trace.complete("tool", "memory_search_trades", "No memories found")
        except Exception:
            trace.complete("tool", "memory_search_lessons", "Skipped")
            trace.complete("tool", "memory_search_trades", "Skipped")

        # ──────────────────────────────────────────────
        # 7. AGENT → Research Agent
        # ──────────────────────────────────────────────
        trace.start("agent", "research")
        format_log("[AGENT START]", "Research Agent")
        research_output = await self.research_agent.analyze(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            technicals=technicals,
            articles=news_articles,
            events=events,
        )
        format_log("[AGENT RESULT]", f"alignment_score={research_output.alignment_score:.2f}")
        format_log("[AGENT COMPLETE]", "Research Agent")
        trace.complete(
            "agent", "research",
            f"Alignment={research_output.alignment_score:.2f}",
            tools_used=["market_data", "technical_analysis", "news_search", "memory_search"],
        )

        # ──────────────────────────────────────────────
        # 8. AGENT → Devil's Advocate Agent
        # ──────────────────────────────────────────────
        trace.start("agent", "devils_advocate")
        format_log("[AGENT START]", "Devil's Advocate Agent")
        devil_output = await self.devil_advocate.challenge(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            research=research_output,
            technicals=technicals,
            memory_items=memory_items,
        )
        format_log("[AGENT RESULT]", f"skepticism_score={devil_output.skepticism_score:.2f}")
        format_log("[AGENT COMPLETE]", "Devil's Advocate Agent")
        trace.complete(
            "agent", "devils_advocate",
            f"Skepticism={devil_output.skepticism_score:.2f}",
            tools_used=["technical_analysis", "news_search", "memory_search", "trade_history"],
        )

        # ──────────────────────────────────────────────
        # 9. AGENT → Decision Agent
        # ──────────────────────────────────────────────
        trace.start("agent", "decision")
        format_log("[AGENT START]", "Decision Agent")
        decision_output = await self.decision_agent.decide(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            research=research_output,
            devils_advocate=devil_output,
            risk=risk_calc,
        )
        format_log("[AGENT RESULT]", f"action={decision_output.action}, confidence={decision_output.confidence:.2f}")
        format_log("[AGENT COMPLETE]", "Decision Agent")
        trace.complete(
            "agent", "decision",
            f"Action={decision_output.action}, Confidence={decision_output.confidence:.2f}",
        )

        return TradeAnalysisResponse(
            symbol=sym,
            direction=req.direction.upper(),
            thesis=req.thesis,
            timeframe=req.timeframe,
            research=research_output,
            devils_advocate=devil_output,
            risk=risk_calc,
            decision=decision_output,
            execution_trace=trace.to_list(),
        )

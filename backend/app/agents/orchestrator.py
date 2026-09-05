import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import (
    TradeAnalysisRequest,
    TradeAnalysisResponse,
)
from app.schemas.risk import RiskCalculationRequest
from app.schemas.memory import MemorySearchResultItem
from app.services.market_data.factory import get_market_data_provider
from app.services.news.factory import get_news_provider
from app.analysis.engine import TechnicalAnalysisEngine
from app.analysis.risk_engine import RiskEngine
from app.services.memory import MemoryService
from app.agents.research_agent import ResearchAgent
from app.agents.devil_advocate_agent import DevilsAdvocateAgent
from app.agents.decision_agent import DecisionAgent


class AgentOrchestrator:
    """
    Multi-Agent Pipeline Orchestrator:
    Coordinates deterministic technical analysis, news sentiment,
    pgvector memory retrieval, quantitative risk calculations,
    and LLM agent deliberation.
    """

    def __init__(self):
        self.market_provider = get_market_data_provider()
        self.news_provider = get_news_provider()
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

        # 1. Fetch Market Bars & Deterministic Technical Analysis
        bars = await self.market_provider.get_historical_bars(sym, timeframe=req.timeframe, limit=100)
        technicals = TechnicalAnalysisEngine.analyze(sym, bars, is_demo=True)

        # 2. Fetch News and Upcoming Catalyst Events
        news_articles = await self.news_provider.get_news_for_symbol(sym, limit=5)
        events = await self.news_provider.get_upcoming_events_for_symbol(sym)


        # 3. Deterministic Quantitative Risk Calculation
        risk_req = RiskCalculationRequest(
            symbol=sym,
            direction=req.direction,
            entry_price=req.entry_price,
            stop_loss=req.stop_loss,
            target_price=req.target_price,
            portfolio_equity=req.portfolio_equity,
            risk_per_trade_pct=req.risk_per_trade_pct,
        )
        risk_calc = RiskEngine.calculate_risk(risk_req)

        # 4. Semantic Search in Trading Memory & Past Lessons
        memory_items = []
        try:
            # Auto-seed default lessons if empty
            await MemoryService.seed_default_lessons(db, user_id)
            lessons = await MemoryService.search_relevant_lessons(db, user_id, req.thesis, top_k=3)
            for l, score in lessons:
                memory_items.append(
                    MemorySearchResultItem(
                        id=str(l.id),
                        type="lesson",
                        title=l.title,
                        content=l.lesson,
                        rule_or_mistake=l.future_rule,
                        similarity_score=score,
                    )
                )
            memories = await MemoryService.search_similar_memories(db, user_id, req.thesis, top_k=3, symbol=sym)
            for m, score in memories:
                memory_items.append(
                    MemorySearchResultItem(
                        id=str(m.id),
                        type="trade_memory",
                        title=m.setup_title,
                        symbol=m.symbol,
                        outcome=m.outcome,
                        content=m.original_thesis,
                        rule_or_mistake=m.mistake or m.lesson,
                        similarity_score=score,
                    )
                )
        except Exception:
            pass

        # 5. Step 1: Research Agent
        research_output = await self.research_agent.analyze(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            technicals=technicals,
            articles=news_articles,
            events=events,
        )

        # 6. Step 2: Devil's Advocate Agent
        devil_output = await self.devil_advocate.challenge(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            research=research_output,
            technicals=technicals,
            memory_items=memory_items,
        )

        # 7. Step 3: Decision Agent Synthesis
        decision_output = await self.decision_agent.decide(
            symbol=sym,
            direction=req.direction,
            thesis=req.thesis,
            research=research_output,
            devils_advocate=devil_output,
            risk=risk_calc,
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
        )

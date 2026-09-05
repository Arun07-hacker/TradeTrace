from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent
from app.schemas.agent import ResearchAgentOutput
from app.schemas.technical import TechnicalAnalysisResult
from app.schemas.news import NewsArticleItem, MarketEventItem


class ResearchAgent(BaseAgent):
    """
    Research Agent:
    Analyzes trader's thesis in the context of deterministic technical indicators,
    support/resistance levels, news catalysts, and market events.
    """

    SYSTEM_PROMPT = """You are the TradeTrace Research Agent.
Your role is to rigorously analyze a trader's hypothesis, combining deterministic technical indicators, support/resistance levels, and recent news catalysts.
Do NOT simply output 'BUY' or 'SELL'. You must remain objective, analytical, and structured.
Output strictly valid JSON with the following structure:
{
    "technical_evaluation": "string summarizing technical indicators, moving averages, RSI, MACD, and volume",
    "catalyst_evaluation": "string summarizing recent news sentiment, upcoming earnings, or macro events",
    "supporting_points": ["point 1", "point 2", "point 3"],
    "risk_points": ["point 1", "point 2", "point 3"],
    "alignment_score": float between 0.0 and 1.0 representing how well the data aligns with the trader's thesis
}
"""

    async def analyze(
        self,
        symbol: str,
        direction: str,
        thesis: str,
        technicals: TechnicalAnalysisResult,
        articles: List[NewsArticleItem],
        events: List[MarketEventItem],
    ) -> ResearchAgentOutput:

        user_content = f"""
Asset: {symbol}
Proposed Direction: {direction}
Trader Thesis: {thesis}

Technical Data:
- Current Price: ${technicals.current_price:.2f}
- Trend: {technicals.trend} (Strength: {technicals.trend_details.strength:.2f})
- Moving Averages: SMA20={technicals.sma_20:.2f}, SMA50={technicals.sma_50:.2f}, SMA200={technicals.sma_200 if technicals.sma_200 else 'N/A'}
- Momentum: RSI(14)={technicals.rsi:.2f}, MACD={technicals.macd.macd:.2f} (Signal: {technicals.macd.signal:.2f}, Hist: {technicals.macd.histogram:.2f})
- Volatility: ATR={technicals.atr:.2f}, Annualized={technicals.volatility_pct:.1f}%
- Support Levels: {', '.join([f'${s:.2f}' for s in technicals.support_resistance.support_levels])}
- Resistance Levels: {', '.join([f'${r:.2f}' for r in technicals.support_resistance.resistance_levels])}

Recent News ({len(articles)} headlines):
{chr(10).join([f'- {a.title} (Sentiment: {a.sentiment_score:+.2f})' for a in articles[:5]])}

Upcoming Events:
{chr(10).join([f'- {e.event_type} on {e.event_date}: {e.title}' for e in events[:3]])}

Evaluate the technical and catalyst environment. Return strictly JSON.
"""

        data = await self.call_llm(self.SYSTEM_PROMPT, user_content)
        return ResearchAgentOutput(
            technical_evaluation=data.get("technical_evaluation", "Technical structure evaluated."),
            catalyst_evaluation=data.get("catalyst_evaluation", "News catalysts evaluated."),
            supporting_points=data.get("supporting_points", []),
            risk_points=data.get("risk_points", []),
            alignment_score=float(data.get("alignment_score", 0.5)),
        )

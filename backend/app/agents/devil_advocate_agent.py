from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent
from app.schemas.agent import DevilsAdvocateOutput, ResearchAgentOutput
from app.schemas.technical import TechnicalAnalysisResult
from app.schemas.memory import MemorySearchResultItem


class DevilsAdvocateAgent(BaseAgent):
    """
    Devil's Advocate Agent:
    Actively attempts to DISPROVE the trader's thesis.
    Exposes confirmation bias, finds counter-indicators, checks trading memory
    for prior matching mistakes, and highlights tail risks.
    """

    SYSTEM_PROMPT = """You are the TradeTrace Devil's Advocate Agent.
Your single mandate is to challenge the trader's thesis and protect their capital from confirmation bias and blind spots.
Actively identify:
1. Bearish counter-indicators if LONG, or bullish counter-indicators if SHORT.
2. Clashes with historical Trading Memory lessons (past mistakes the trader made in similar setups).
3. Hidden catalyst risks, liquidity traps, and false breakout vulnerability.
4. Specific indications that the trader is succumbing to confirmation bias or FOMO.

Output strictly valid JSON with this structure:
{
    "counter_arguments": ["argument 1", "argument 2", "argument 3"],
    "hidden_risks": ["risk 1", "risk 2"],
    "confirmation_bias_warning": "specific warning explaining what the trader is ignoring",
    "historical_memory_conflicts": ["warning 1 referencing past lessons"],
    "skepticism_score": float between 0.0 and 1.0 (higher means higher doubt/risk of trap)
}
"""

    async def challenge(
        self,
        symbol: str,
        direction: str,
        thesis: str,
        research: ResearchAgentOutput,
        technicals: TechnicalAnalysisResult,
        memory_items: List[MemorySearchResultItem],
    ) -> DevilsAdvocateOutput:
        mem_text = "\n".join([
            f"- [{item.type.upper()}] {item.title}: {item.rule_or_mistake or item.content} (Similarity: {item.similarity_score:.2f})"
            for item in memory_items[:4]
        ]) or "No direct past memory conflicts found."

        user_content = f"""
Asset: {symbol}
Proposed Direction: {direction}
Trader Thesis: {thesis}

Research Agent Findings:
- Technical Eval: {research.technical_evaluation}
- Risk Points: {', '.join(research.risk_points)}
- Alignment Score: {research.alignment_score:.2f}

Technical Metrics:
- Trend: {technicals.trend} (Strength: {technicals.trend_details.strength:.2f})
- RSI: {technicals.rsi:.2f}
- MACD Histogram: {technicals.macd.histogram:.2f}
- ATR: ${technicals.atr:.2f}


Relevant Trading Memory & Past Lessons:
{mem_text}

Challenge this trade thesis thoroughly. Expose confirmation bias and traps. Output strictly JSON.
"""
        data = await self.call_llm(self.SYSTEM_PROMPT, user_content)
        return DevilsAdvocateOutput(
            counter_arguments=data.get("counter_arguments", []),
            hidden_risks=data.get("hidden_risks", []),
            confirmation_bias_warning=data.get(
                "confirmation_bias_warning",
                "Be vigilant of confirmation bias when sizing your position.",
            ),
            historical_memory_conflicts=data.get("historical_memory_conflicts", []),
            skepticism_score=float(data.get("skepticism_score", 0.5)),
        )

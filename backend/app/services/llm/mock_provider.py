import json
import re
from typing import List
from app.services.llm.base import LLMProvider, LLMMessage


class MockLLMProvider(LLMProvider):
    """
    Mock LLM Provider for offline evaluation and deterministic testing.
    Parses prompt context and outputs valid structured JSON simulating
    specialized trading intelligence agents.
    """

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str:
        sys_text = " ".join([m.content for m in messages if m.role == "system"]).lower()
        full_text = " ".join([m.content for m in messages]).lower()

        # 1. Devil's Advocate Agent request
        if "devil's advocate" in sys_text or "challenge" in sys_text or "skepticism" in sys_text:
            return json.dumps({
                "counter_arguments": [
                    "The proposed setup relies heavily on breakout continuation into multi-month structural resistance without confirmed volume follow-through.",
                    "Risk/Reward asymmetry is compromised if broader index exhibits sudden midday liquidity pullbacks.",
                    "Trader thesis shows indications of confirmation bias by overlooking deceleration in relative volume."
                ],
                "hidden_risks": [
                    "Imminent sector earnings announcements may induce extreme implied volatility skew.",
                    "Order book liquidity clusters indicate potential spoofing near the target take-profit level."
                ],
                "confirmation_bias_warning": "Warning: The thesis selectively focuses on trendline retests while neglecting RSI divergence and lower-high distribution on intermediate 4-hour candles.",
                "historical_memory_conflicts": [
                    "Trading Memory Alert: Similar breakout setups entered into overhead resistance suffered an average stop-out rate of 68% in previous paper journal records."
                ],
                "skepticism_score": 0.68
            })

        # 2. Decision Agent request
        elif "decision agent" in sys_text or "decision" in sys_text:
            return json.dumps({
                "action": "PROCEED_WITH_CAUTION",
                "thesis_strength": 0.71,
                "confidence": 0.65,
                "summary": "The trade thesis demonstrates valid technical alignment above dynamic support, but Devil's Advocate highlights substantial resistance overhead and memory conflict. Execution is viable strictly with disciplined 1% risk allocation and strict stop adherence.",
                "supporting_factors": [
                    "Technical indicators confirm prevailing trend structure above 50 SMA",
                    "Positive R:R profile satisfies minimum required 1:1.5 threshold",
                    "Volume expansion confirms preliminary buyer interest"
                ],
                "risk_factors": [
                    "Proximity to major overhead resistance band",
                    "Historical memory warning on similar breakout failures",
                    "Macro catalyst event scheduled within swing trading window"
                ],
                "devils_advocate_findings": [
                    "Confirmation bias identified regarding resistance momentum",
                    "Potential false breakout trap if volume fails to sustain above opening range"
                ],
                "memory_warnings": [
                    "Previous lesson: Never chase momentum breakouts directly into overhead daily resistance without waiting for structural confirmation."
                ],
                "suggested_modifications": [
                    "Wait for a 1-day candle close above resistance before initiating full planned position.",
                    "Consider scaling in with 50% initial size and adding remainder upon confirmed pullback support test."
                ]
            })

        # 3. Research Agent request
        elif "research agent" in sys_text or "research" in sys_text:
            return json.dumps({
                "technical_evaluation": "Price is testing the upper boundary of its intermediate regression channel with expanding volume on the daily timeframe. Moving averages reflect positive medium-term momentum (20 SMA > 50 SMA), though short-term oscillators indicate approaching overbought terrain (RSI ~62).",
                "catalyst_evaluation": "Recent corporate earnings and guidance remain moderately constructive, though macroeconomic sector headwinds and yield volatility pose intermittent pressure.",
                "supporting_points": [
                    "Sustained price consolidation above primary dynamic support (20-day SMA)",
                    "Bullish moving average convergence (MACD histogram expansion)",
                    "Institutional accumulation volume visible on upward daily sessions"
                ],
                "risk_points": [
                    "Overhead resistance zone located within 2.5% of proposed entry",
                    "Sector rotation risk if upcoming macroeconomic inflation prints surprise to upside",
                    "ATR volatility expansion may threaten tight stop placements"
                ],
                "alignment_score": 0.74
            })


        # 4. Post-Trade Autopsy Agent request
        elif "autopsy" in sys_text or "post-trade" in sys_text or "autopsy" in full_text:

            return json.dumps({
                "execution_grade": "B-",
                "discipline_score": 0.72,
                "key_mistake": "Failed to take partial profits at R1 resistance, allowing a winning trade to retrace into stop-loss.",
                "lesson_learned": "When price reaches 2R target with stalling momentum, trail stop to breakeven or lock in 50% position size.",
                "actionable_rule": "Enforce trailing stop to entry price once unrealized profit exceeds 1.5R."
            })

        # Generic fallback
        return json.dumps({
            "status": "completed",
            "message": "Processed mock intelligence response."
        })

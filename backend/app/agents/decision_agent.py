from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent
from app.schemas.agent import DecisionAgentOutput, ResearchAgentOutput, DevilsAdvocateOutput
from app.schemas.risk import RiskCalculationResponse


class DecisionAgent(BaseAgent):
    """
    Decision Synthesis Agent:
    Synthesizes research, devil's advocate, and deterministic risk parameters.
    Does NOT predict future prices and does NOT output BUY/SELL recommendations.
    Outputs an explainable, risk-conscious operational assessment.
    """

    SYSTEM_PROMPT = """You are the TradeTrace Decision Agent.
Your role is to produce a balanced, explainable, and capital-preserving decision assessment for the trader.
CRITICAL MANDATE:
1. Do NOT issue 'BUY' or 'SELL' signals.
2. Do NOT predict stock prices.
3. Suggest one of the following actions:
   - 'PROCEED_WITH_CAUTION': Solid setup, favorable risk/reward, risks are manageable with strict stop discipline.
   - 'WAIT_FOR_CONFIRMATION': Viable thesis but key levels are unconfirmed or incoming catalyst warrants waiting.
   - 'REVISE_PARAMETERS': Invalid geometric parameters, unfavorable risk/reward, or excessive portfolio exposure.
   - 'REJECT': Severe memory conflict, extreme skepticism, unviable risk structure, or high probability trap.

Output strictly valid JSON with the following structure:
{
    "action": "PROCEED_WITH_CAUTION | WAIT_FOR_CONFIRMATION | REVISE_PARAMETERS | REJECT",
    "thesis_strength": float between 0.0 and 1.0,
    "confidence": float between 0.0 and 1.0,
    "summary": "comprehensive synthesis of technical, catalyst, devil advocate, and risk evaluations",
    "supporting_factors": ["factor 1", "factor 2"],
    "risk_factors": ["risk 1", "risk 2"],
    "devils_advocate_findings": ["finding 1", "finding 2"],
    "memory_warnings": ["warning 1"],
    "suggested_modifications": ["actionable advice 1", "actionable advice 2"]
}
"""

    async def decide(
        self,
        symbol: str,
        direction: str,
        thesis: str,
        research: ResearchAgentOutput,
        devils_advocate: DevilsAdvocateOutput,
        risk: RiskCalculationResponse,
    ) -> DecisionAgentOutput:
        # Override action to REVISE_PARAMETERS if deterministic risk engine flagged invalid geometry
        if not risk.is_valid:
            default_action = "REVISE_PARAMETERS"
        elif devils_advocate.skepticism_score > 0.85:
            default_action = "REJECT"
        else:
            default_action = "PROCEED_WITH_CAUTION"

        user_content = f"""
Asset: {symbol}
Direction: {direction}
Trader's Original Thesis: {thesis}

Deterministic Risk Evaluation:
- Stop Loss: ${risk.stop_loss:.2f} (Entry: ${risk.entry_price:.2f}, Target: ${risk.target:.2f})
- Risk/Reward Ratio: 1:{risk.risk_reward_ratio:.2f}
- Position Size: {risk.position_size} shares (${risk.position_value:,.2f}, {risk.portfolio_exposure_pct:.1f}% exposure)
- Risk Level: {risk.risk_level.upper()}
- Valid Geometry: {risk.is_valid}
- Warnings: {', '.join(risk.warnings) if risk.warnings else 'None'}

Research Agent Assessment:
- Technical Summary: {research.technical_evaluation}
- Catalyst Summary: {research.catalyst_evaluation}
- Alignment Score: {research.alignment_score:.2f}

Devil's Advocate Challenges:
- Counter Arguments: {', '.join(devils_advocate.counter_arguments)}
- Confirmation Bias Warning: {devils_advocate.confirmation_bias_warning}
- Memory Conflicts: {', '.join(devils_advocate.historical_memory_conflicts)}
- Skepticism Score: {devils_advocate.skepticism_score:.2f}

Synthesize these findings and produce the final assessment JSON.
"""
        data = await self.call_llm(self.SYSTEM_PROMPT, user_content)

        action = data.get("action", default_action)
        if not risk.is_valid:
            action = "REVISE_PARAMETERS"

        return DecisionAgentOutput(
            action=action,
            thesis_strength=float(data.get("thesis_strength", 0.65)),
            confidence=float(data.get("confidence", 0.60)),
            summary=data.get("summary", "Synthesis of multi-agent intelligence completed."),
            supporting_factors=data.get("supporting_factors", research.supporting_points),
            risk_factors=data.get("risk_factors", research.risk_points),
            devils_advocate_findings=data.get("devils_advocate_findings", devils_advocate.counter_arguments),
            memory_warnings=data.get("memory_warnings", devils_advocate.historical_memory_conflicts),
            suggested_modifications=data.get("suggested_modifications", []),
        )

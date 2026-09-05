import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.agents.base import BaseAgent
from app.models.trade import Trade, TradeMemory
from app.schemas.autopsy import TradeAutopsyResponse
from app.services.memory import MemoryService


class AutopsyAgent(BaseAgent):
    """
    Post-Trade Autopsy & Learning Agent:
    Analyzes closed paper trades, diagnoses execution errors,
    formulates actionable future rules, and commits them to pgvector memory.
    """

    SYSTEM_PROMPT = """You are the TradeTrace Post-Trade Autopsy Agent.
Your mandate is to perform an honest, rigorous post-mortem on a closed trade.
Evaluate:
1. Did the trader adhere to their stop-loss and profit targets?
2. Did emotional bias (FOMO, fear, impatience, greed) interfere with execution?
3. What is the fundamental root-cause mistake or edge that determined the outcome?
4. What is the permanent, actionable future rule that prevents this mistake from recurring?

Output strictly valid JSON:
{
    "execution_grade": "A | B | C | D | F",
    "discipline_score": float between 0.0 and 1.0,
    "key_mistake": "specific tactical mistake or psychological flaw",
    "lesson_learned": "in-depth lesson learned from this trade lifecycle",
    "future_rule": "concrete actionable rule to adhere to on all future setups"
}
"""

    async def analyze_and_index(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        trader_notes: Optional[str] = None,
    ) -> TradeAutopsyResponse:
        stmt = (
            select(Trade)
            .options(selectinload(Trade.events), selectinload(Trade.memory))
            .where(Trade.id == trade_id, Trade.user_id == user_id)
        )
        res = await db.execute(stmt)
        trade = res.scalar_one_or_none()
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        if trade.status == "OPEN":
            raise HTTPException(status_code=400, detail="Cannot run autopsy on an OPEN trade. Close the trade first.")

        pnl = trade.realized_pnl or 0.0
        pnl_pct = trade.realized_pnl_pct or 0.0
        outcome = "WIN" if pnl > 0 else ("LOSS" if pnl < 0 else "BREAKEVEN")

        user_content = f"""
Asset: {trade.symbol}
Direction: {trade.direction}
Initial Entry: ${trade.entry_price:.2f}
Exit Price: ${trade.exit_price or trade.entry_price:.2f}
Stop Loss: ${trade.stop_loss:.2f}
Target: ${trade.target:.2f}
Realized PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)
Status / Close Reason: {trade.status}
Original Thesis: {trade.thesis}
Trader Post-Mortem Notes: {trader_notes or 'None provided'}

Execution Events:
{chr(10).join([f'- [{e.event_type}] {e.description}' for e in trade.events])}

Produce post-mortem evaluation JSON.
"""
        data = await self.call_llm(self.SYSTEM_PROMPT, user_content)

        grade = data.get("execution_grade", "B")
        score = float(data.get("discipline_score", 0.70))
        mistake = data.get("key_mistake", "No major mistake identified.")
        lesson = data.get("lesson_learned", "Continue disciplined risk-first execution.")
        future_rule = data.get("future_rule", "Adhere strictly to planned stop-loss and take-profit targets.")

        # Index into Cognitive Trading Memory
        try:
            await MemoryService.index_trade_memory(
                db=db,
                user_id=user_id,
                trade_id=trade.id,
                symbol=trade.symbol,
                setup_title=f"{trade.symbol} {trade.direction} Setup",
                original_thesis=trade.thesis,
                setup_tags=[trade.symbol, trade.direction, outcome],
                outcome=outcome,
                mistake=mistake,
                lesson=lesson,
            )

            # Also create persistent TradeLesson
            await MemoryService.index_trade_lesson(
                db=db,
                user_id=user_id,
                title=f"{trade.symbol} {outcome}: {mistake[:50]}",
                setup_type=f"{trade.direction} Swing",
                mistake_type=mistake[:40],
                lesson=lesson,
                future_rule=future_rule,
                trade_id=trade.id,
            )
        except Exception:
            pass  # Avoid failure if already indexed

        return TradeAutopsyResponse(
            trade_id=trade.id,
            symbol=trade.symbol,
            outcome=outcome,
            realized_pnl=pnl,
            realized_pnl_pct=pnl_pct,
            execution_grade=grade,
            discipline_score=score,
            key_mistake=mistake,
            lesson_learned=lesson,
            future_rule=future_rule,
            indexed_in_memory=True,
        )

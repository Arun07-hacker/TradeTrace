import uuid
from typing import List, Tuple, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.trade import TradeLesson, TradeMemory
from app.services.memory.embedding import EmbeddingService


DEFAULT_LESSONS = [
    {
        "title": "Earnings Roulette: Chasing Breakouts Right Before Reports",
        "setup_type": "Earnings Momentum",
        "mistake_type": "Catalyst Roulette / Blind Speculation",
        "lesson": "Entering a high-volatility momentum breakout less than 48 hours prior to an earnings announcement turns a disciplined setup into a 50/50 binary gamble with catastrophic IV crush risk.",
        "future_rule": "NEVER enter a directional swing trade within 48 hours of an unhedged company earnings announcement.",
    },
    {
        "title": "Averaging Down on Systematic Technical Breakdown",
        "setup_type": "Mean Reversion",
        "mistake_type": "Sunk Cost Bias / Ignoring Invalidation",
        "lesson": "Adding shares to a losing position when the key support level has cracked converts a controlled 1% portfolio risk into a devastating multi-thousand dollar account drawdown.",
        "future_rule": "The stop-loss is ABSOLUTE. Never add size to an underwater position once the original structural thesis is invalidated.",
    },
    {
        "title": "Timeframe Myopia: Trading 5-Min Breakout Directly into Daily Resistance",
        "setup_type": "Day Trading Breakout",
        "mistake_type": "Ignoring Higher-Timeframe Structure",
        "lesson": "A strong 5-minute green candle looks explosive in isolation, but will instantly stall and reverse when slamming directly into multi-month daily/weekly supply overhead.",
        "future_rule": "Always verify Daily and 4-Hour key resistance levels before taking breakout entries on lower intraday timeframes.",
    },
    {
        "title": "Revenge Trading After Consecutive Stop-Outs",
        "setup_type": "Scalp / Momentum",
        "mistake_type": "Emotional Tilt & Oversizing",
        "lesson": "Immediately re-entering the market after two rapid stop-outs to 'win back' money leads to poor entry criteria, widened stops, and exponential portfolio decay.",
        "future_rule": "Enforce a mandatory 3-hour trading freeze or shut down terminal after 2 consecutive stop-outs in a single trading session.",
    },
    {
        "title": "Holding Losing Position Hoping to Exit at Breakeven",
        "setup_type": "Trend Following",
        "mistake_type": "Loss Aversion / Breakeven Hope",
        "lesson": "Refusing to take a small planned loss because of hope that price will rebound back to breakeven allows a minor scrape to transform into a catastrophic portfolio hole.",
        "future_rule": "If price crosses your predetermined stop-loss level, close the paper trade immediately without emotional hesitation.",
    },
]


class MemoryService:
    """
    Cognitive Trading Memory Service.
    Stores lessons, tracks trade autopsies, and runs semantic vector search
    to prevent traders from repeating previous mistakes.
    """

    @classmethod
    async def index_trade_lesson(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        setup_type: str,
        mistake_type: str,
        lesson: str,
        future_rule: str,
        trade_id: Optional[uuid.UUID] = None,
        times_applied: int = 1,
    ) -> TradeLesson:
        text_to_embed = f"{title} | {setup_type} | {mistake_type} | {lesson} | {future_rule}"
        embedding = await EmbeddingService.get_embedding(text_to_embed)

        db_lesson = TradeLesson(
            user_id=user_id,
            trade_id=trade_id,
            title=title.strip(),
            setup_type=setup_type.strip(),
            mistake_type=mistake_type.strip(),
            lesson=lesson.strip(),
            future_rule=future_rule.strip(),
            times_applied=times_applied,
            embedding=embedding,
        )
        db.add(db_lesson)
        await db.commit()
        await db.refresh(db_lesson)
        return db_lesson

    @classmethod
    async def index_trade_memory(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        symbol: str,
        setup_title: str,
        original_thesis: str,
        setup_tags: List[str],
        outcome: str = "PENDING",
        mistake: Optional[str] = None,
        lesson: Optional[str] = None,
        market_context: Optional[Any] = None,
        devils_advocate_warnings: Optional[List[str]] = None,
    ) -> TradeMemory:
        text_to_embed = f"{symbol} {setup_title} {' '.join(setup_tags)} {original_thesis} {mistake or ''} {lesson or ''}"
        embedding = await EmbeddingService.get_embedding(text_to_embed)

        memory = TradeMemory(
            user_id=user_id,
            trade_id=trade_id,
            symbol=symbol.upper(),
            setup_title=setup_title,
            original_thesis=original_thesis,
            setup_tags=setup_tags or [],
            market_context=market_context,
            devils_advocate_warnings=devils_advocate_warnings or [],
            outcome=outcome.upper(),
            mistake=mistake,
            lesson=lesson,
            embedding=embedding,
        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        return memory

    @classmethod
    async def search_relevant_lessons(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        setup_type: Optional[str] = None,
    ) -> List[Tuple[TradeLesson, float]]:
        stmt = select(TradeLesson).where(TradeLesson.user_id == user_id)
        if setup_type:
            stmt = stmt.where(TradeLesson.setup_type.ilike(f"%{setup_type}%"))
        
        result = await db.execute(stmt)
        lessons = result.scalars().all()

        if not lessons:
            return []

        query_vec = await EmbeddingService.get_embedding(query)
        scored: List[Tuple[TradeLesson, float]] = []

        for lesson in lessons:
            if lesson.embedding:
                score = EmbeddingService.cosine_similarity(query_vec, lesson.embedding)
            else:
                score = 0.0
            scored.append((lesson, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @classmethod
    async def search_similar_memories(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        query: str,
        top_k: int = 5,
        symbol: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> List[Tuple[TradeMemory, float]]:
        stmt = select(TradeMemory).where(TradeMemory.user_id == user_id)
        if symbol:
            stmt = stmt.where(TradeMemory.symbol == symbol.upper())
        if outcome:
            stmt = stmt.where(TradeMemory.outcome == outcome.upper())

        result = await db.execute(stmt)
        memories = result.scalars().all()

        if not memories:
            return []

        query_vec = await EmbeddingService.get_embedding(query)
        scored: List[Tuple[TradeMemory, float]] = []

        for mem in memories:
            if mem.embedding:
                score = EmbeddingService.cosine_similarity(query_vec, mem.embedding)
            else:
                score = 0.0
            scored.append((mem, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @classmethod
    async def seed_default_lessons(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> List[TradeLesson]:
        # Check if user already has lessons
        stmt = select(TradeLesson).where(TradeLesson.user_id == user_id)
        existing = (await db.execute(stmt)).scalars().all()
        if existing:
            return existing

        created = []
        for d in DEFAULT_LESSONS:
            lesson = await cls.index_trade_lesson(
                db=db,
                user_id=user_id,
                title=d["title"],
                setup_type=d["setup_type"],
                mistake_type=d["mistake_type"],
                lesson=d["lesson"],
                future_rule=d["future_rule"],
            )
            created.append(lesson)
        return created

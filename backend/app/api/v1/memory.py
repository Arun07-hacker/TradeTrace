from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.trade import TradeLesson, TradeMemory
from app.schemas.memory import (
    TradeLessonResponse,
    TradeLessonCreate,
    TradeMemoryResponse,
    MemorySearchResponse,
    MemorySearchResultItem,
)
from app.services.memory import MemoryService

router = APIRouter(prefix="/memory", tags=["Trading Memory Engine"])


@router.get("/search", response_model=MemorySearchResponse)
async def search_trading_memory(
    q: str = Query(..., min_length=2, description="Semantic query to match against trading memory and lessons"),
    limit: int = Query(5, ge=1, le=20, description="Max results per category"),
    symbol: Optional[str] = Query(None, description="Optional symbol filter"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search trading memory using semantic vector similarity.
    Retrieves previous similar trade mistakes, counter-arguments, and preventative rules
    to display in the Devil's Advocate / Pre-trade analysis.
    """
    # Auto-seed default lessons if user has none
    await MemoryService.seed_default_lessons(db, current_user.id)

    lessons_scored = await MemoryService.search_relevant_lessons(
        db=db,
        user_id=current_user.id,
        query=q,
        top_k=limit,
    )

    memories_scored = await MemoryService.search_similar_memories(
        db=db,
        user_id=current_user.id,
        query=q,
        top_k=limit,
        symbol=symbol,
    )

    results: List[MemorySearchResultItem] = []

    for lesson, score in lessons_scored:
        results.append(
            MemorySearchResultItem(
                id=str(lesson.id),
                type="lesson",
                title=lesson.title,
                content=lesson.lesson,
                rule_or_mistake=lesson.future_rule,
                similarity_score=score,
            )
        )

    for mem, score in memories_scored:
        results.append(
            MemorySearchResultItem(
                id=str(mem.id),
                type="trade_memory",
                title=mem.setup_title,
                symbol=mem.symbol,
                outcome=mem.outcome,
                content=mem.original_thesis,
                rule_or_mistake=mem.mistake or mem.lesson,
                similarity_score=score,
            )
        )

    # Sort combined results by similarity score descending
    results.sort(key=lambda x: x.similarity_score, reverse=True)

    return MemorySearchResponse(
        query=q,
        total_results=len(results),
        results=results,
    )


@router.get("/lessons", response_model=List[TradeLessonResponse])
async def list_trade_lessons(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all operational rules and post-mortem lessons for the current user."""
    # Ensure default lessons exist
    await MemoryService.seed_default_lessons(db, current_user.id)

    stmt = (
        select(TradeLesson)
        .where(TradeLesson.user_id == current_user.id)
        .order_by(TradeLesson.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/lessons", response_model=TradeLessonResponse, status_code=status.HTTP_201_CREATED)
async def create_trade_lesson(
    payload: TradeLessonCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a new post-trade lesson with automated semantic vector embedding."""
    lesson = await MemoryService.index_trade_lesson(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        setup_type=payload.setup_type,
        mistake_type=payload.mistake_type,
        lesson=payload.lesson,
        future_rule=payload.future_rule,
        trade_id=payload.trade_id,
    )
    return lesson


@router.post("/seed", response_model=List[TradeLessonResponse])
async def seed_lessons(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Force seed default cognitive trading lessons if not already present."""
    return await MemoryService.seed_default_lessons(db, current_user.id)


@router.get("/history", response_model=List[TradeMemoryResponse])
async def list_trade_memories(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve indexed trade memory records and autopsy histories."""
    stmt = (
        select(TradeMemory)
        .where(TradeMemory.user_id == current_user.id)
        .order_by(TradeMemory.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

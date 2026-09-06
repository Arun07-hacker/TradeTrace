import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base import ToolResult, log_tool_execution
from app.services.memory import MemoryService
from app.schemas.memory import MemorySearchResultItem


@log_tool_execution("memory_search.search_similar_trades")
async def search_similar_trades(
    db: AsyncSession,
    user_id: uuid.UUID,
    thesis: str,
    symbol: Optional[str] = None,
    top_k: int = 3,
) -> ToolResult:
    """Search trading memory for historically similar trade setups."""
    try:
        results = await MemoryService.search_similar_memories(
            db=db, user_id=user_id, query=thesis, top_k=top_k, symbol=symbol,
        )
        items = []
        for mem, score in results:
            items.append(
                MemorySearchResultItem(
                    id=str(mem.id),
                    type="trade_memory",
                    title=mem.setup_title,
                    symbol=mem.symbol,
                    outcome=mem.outcome,
                    content=mem.original_thesis,
                    rule_or_mistake=mem.mistake or mem.lesson,
                    similarity_score=score,
                ).model_dump()
            )
        return ToolResult(
            tool="memory_search.search_similar_trades",
            status="success",
            data=items,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="memory_search.search_similar_trades",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("memory_search.get_previous_lessons")
async def get_previous_lessons(
    db: AsyncSession,
    user_id: uuid.UUID,
    thesis: str,
    top_k: int = 3,
) -> ToolResult:
    """Retrieve relevant trading lessons from the cognitive memory vault."""
    try:
        # Auto-seed default lessons if empty
        await MemoryService.seed_default_lessons(db, user_id)
        results = await MemoryService.search_relevant_lessons(
            db=db, user_id=user_id, query=thesis, top_k=top_k,
        )
        items = []
        for lesson, score in results:
            items.append(
                MemorySearchResultItem(
                    id=str(lesson.id),
                    type="lesson",
                    title=lesson.title,
                    content=lesson.lesson,
                    rule_or_mistake=lesson.future_rule,
                    similarity_score=score,
                ).model_dump()
            )
        return ToolResult(
            tool="memory_search.get_previous_lessons",
            status="success",
            data=items,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="memory_search.get_previous_lessons",
            status="error",
            data=None,
            error=str(e),
        )

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tools.base import ToolResult, log_tool_execution
from app.services.trading.paper_engine import PaperTradingEngine
from app.models.trade import Trade


@log_tool_execution("trade_history.get_trade_history")
async def get_trade_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    symbol: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> ToolResult:
    """Retrieve paper trade history with optional symbol and status filters."""
    try:
        trades = await PaperTradingEngine.list_trades(
            db=db,
            user_id=user_id,
            status_filter=status_filter,
            symbol_filter=symbol,
        )
        trades_data = []
        for t in trades:
            trades_data.append({
                "id": str(t.id),
                "symbol": t.symbol,
                "direction": t.direction,
                "entry_price": t.entry_price,
                "stop_loss": t.stop_loss,
                "target": t.target,
                "quantity": t.quantity,
                "thesis": t.thesis,
                "status": t.status,
                "exit_price": t.exit_price,
                "realized_pnl": t.realized_pnl,
                "realized_pnl_pct": t.realized_pnl_pct,
                "created_at": str(t.created_at),
            })
        return ToolResult(
            tool="trade_history.get_trade_history",
            status="success",
            data=trades_data,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="trade_history.get_trade_history",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("trade_history.get_trade_details")
async def get_trade_details(
    db: AsyncSession,
    user_id: uuid.UUID,
    trade_id: uuid.UUID,
) -> ToolResult:
    """Retrieve detailed information about a specific paper trade including events."""
    try:
        stmt = (
            select(Trade)
            .options(selectinload(Trade.events))
            .where(Trade.id == trade_id, Trade.user_id == user_id)
        )
        result = await db.execute(stmt)
        trade = result.scalar_one_or_none()
        if not trade:
            return ToolResult(
                tool="trade_history.get_trade_details",
                status="error",
                data=None,
                error=f"Trade {trade_id} not found for user {user_id}",
            )

        events_data = []
        for e in trade.events:
            events_data.append({
                "id": str(e.id),
                "event_type": e.event_type,
                "description": e.description,
                "severity": e.severity,
                "created_at": str(e.created_at),
            })

        return ToolResult(
            tool="trade_history.get_trade_details",
            status="success",
            data={
                "id": str(trade.id),
                "symbol": trade.symbol,
                "direction": trade.direction,
                "timeframe": trade.timeframe,
                "entry_price": trade.entry_price,
                "stop_loss": trade.stop_loss,
                "target": trade.target,
                "quantity": trade.quantity,
                "risk_amount": trade.risk_amount,
                "risk_reward_ratio": trade.risk_reward_ratio,
                "thesis": trade.thesis,
                "decision": trade.decision,
                "status": trade.status,
                "exit_price": trade.exit_price,
                "realized_pnl": trade.realized_pnl,
                "realized_pnl_pct": trade.realized_pnl_pct,
                "events": events_data,
                "created_at": str(trade.created_at),
            },
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="trade_history.get_trade_details",
            status="error",
            data=None,
            error=str(e),
        )

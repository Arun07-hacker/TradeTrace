import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base import ToolResult, log_tool_execution
from app.services.trading.paper_engine import PaperTradingEngine
from app.schemas.trade import TradeCreate, TradeCloseRequest


@log_tool_execution("paper_trade.create_paper_trade")
async def create_paper_trade(
    db: AsyncSession,
    user_id: uuid.UUID,
    symbol: str,
    direction: str,
    entry_price: float,
    stop_loss: float,
    target: float,
    quantity: float,
    thesis: str,
    decision: str = "PROCEED_WITH_CAUTION",
    timeframe: str = "1d",
) -> ToolResult:
    """Execute a new paper trade through the PaperTradingEngine."""
    try:
        req = TradeCreate(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target=target,
            quantity=quantity,
            thesis=thesis,
            decision=decision,
        )
        trade = await PaperTradingEngine.execute_trade(db=db, user_id=user_id, req=req)
        return ToolResult(
            tool="paper_trade.create_paper_trade",
            status="success",
            data={
                "trade_id": str(trade.id),
                "symbol": trade.symbol,
                "direction": trade.direction,
                "entry_price": trade.entry_price,
                "stop_loss": trade.stop_loss,
                "target": trade.target,
                "quantity": trade.quantity,
                "status": trade.status,
                "risk_amount": trade.risk_amount,
                "risk_reward_ratio": trade.risk_reward_ratio,
            },
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="paper_trade.create_paper_trade",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("paper_trade.close_paper_trade")
async def close_paper_trade(
    db: AsyncSession,
    user_id: uuid.UUID,
    trade_id: uuid.UUID,
    exit_price: Optional[float] = None,
    reason: str = "CLOSED_MANUALLY",
) -> ToolResult:
    """Close an existing open paper trade."""
    try:
        req = TradeCloseRequest(exit_price=exit_price, reason=reason)
        trade = await PaperTradingEngine.close_trade(
            db=db, user_id=user_id, trade_id=trade_id, req=req,
        )
        return ToolResult(
            tool="paper_trade.close_paper_trade",
            status="success",
            data={
                "trade_id": str(trade.id),
                "symbol": trade.symbol,
                "status": trade.status,
                "exit_price": trade.exit_price,
                "realized_pnl": trade.realized_pnl,
                "realized_pnl_pct": trade.realized_pnl_pct,
            },
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="paper_trade.close_paper_trade",
            status="error",
            data=None,
            error=str(e),
        )

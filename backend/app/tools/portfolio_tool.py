import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.base import ToolResult, log_tool_execution
from app.services.trading.paper_engine import PaperTradingEngine


@log_tool_execution("portfolio.get_portfolio")
async def get_portfolio(db: AsyncSession, user_id: uuid.UUID) -> ToolResult:
    """Retrieve full paper trading portfolio summary with current positions."""
    try:
        portfolio = await PaperTradingEngine.get_portfolio_summary(db=db, user_id=user_id)
        data = {
            "id": str(portfolio.id),
            "user_id": str(portfolio.user_id),
            "initial_balance": portfolio.initial_balance,
            "cash_balance": portfolio.cash_balance,
            "total_equity": portfolio.total_equity,
            "realized_pnl": portfolio.realized_pnl,
            "unrealized_pnl": portfolio.unrealized_pnl,
            "win_count": portfolio.win_count,
            "loss_count": portfolio.loss_count,
            "max_drawdown_pct": portfolio.max_drawdown_pct,
            "current_exposure_pct": portfolio.current_exposure_pct,
            "positions_count": len(portfolio.positions),
        }
        return ToolResult(
            tool="portfolio.get_portfolio",
            status="success",
            data=data,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="portfolio.get_portfolio",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("portfolio.get_open_positions")
async def get_open_positions(db: AsyncSession, user_id: uuid.UUID) -> ToolResult:
    """List all currently open paper trading positions."""
    try:
        trades = await PaperTradingEngine.list_trades(
            db=db, user_id=user_id, status_filter="OPEN",
        )
        positions = []
        for t in trades:
            positions.append({
                "id": str(t.id),
                "symbol": t.symbol,
                "direction": t.direction,
                "entry_price": t.entry_price,
                "stop_loss": t.stop_loss,
                "target": t.target,
                "quantity": t.quantity,
                "thesis": t.thesis,
                "status": t.status,
            })
        return ToolResult(
            tool="portfolio.get_open_positions",
            status="success",
            data=positions,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="portfolio.get_open_positions",
            status="error",
            data=None,
            error=str(e),
        )

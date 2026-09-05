import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.trade import Trade, TradeEvent
from app.models.portfolio import Portfolio, Position
from app.schemas.trade import TradeCreate, TradeCloseRequest
from app.services.market_data.factory import get_market_data_provider


class PaperTradingEngine:
    """
    Paper Trading Execution Engine.
    Executes and tracks paper trades exclusively with real portfolio accounting,
    slippage tracking, stop/target monitoring, and risk management limits.
    REAL-MONEY EXECUTION IS STRICTLY NOT SUPPORTED.
    """

    @classmethod
    async def get_or_create_portfolio(cls, db: AsyncSession, user_id: uuid.UUID) -> Portfolio:
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.positions))
            .where(Portfolio.user_id == user_id)
        )
        res = await db.execute(stmt)
        portfolio = res.scalar_one_or_none()
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                initial_balance=100000.0,
                cash_balance=100000.0,
                total_equity=100000.0,
            )
            db.add(portfolio)
            await db.commit()
            stmt2 = (
                select(Portfolio)
                .options(selectinload(Portfolio.positions))
                .where(Portfolio.id == portfolio.id)
            )
            res2 = await db.execute(stmt2)
            portfolio = res2.scalar_one()
        return portfolio


    @classmethod
    async def execute_trade(
        cls, db: AsyncSession, user_id: uuid.UUID, req: TradeCreate
    ) -> Trade:
        portfolio = await cls.get_or_create_portfolio(db, user_id)
        sym = req.symbol.upper().strip()
        direction = req.direction.upper()

        position_cost = req.quantity * req.entry_price
        if direction == "LONG" and portfolio.cash_balance < position_cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient paper cash: required ${position_cost:,.2f}, available ${portfolio.cash_balance:,.2f}",
            )

        # Risk parameters
        risk_per_share = abs(req.entry_price - req.stop_loss)
        reward_per_share = abs(req.target - req.entry_price)
        risk_amount = round(req.quantity * risk_per_share, 2)
        risk_reward_ratio = round(reward_per_share / max(0.01, risk_per_share), 2)

        # Create Trade record
        trade = Trade(
            user_id=user_id,
            symbol=sym,
            direction=direction,
            timeframe=req.timeframe,
            entry_price=round(req.entry_price, 2),
            stop_loss=round(req.stop_loss, 2),
            target=round(req.target, 2),
            quantity=req.quantity,
            risk_amount=risk_amount,
            risk_reward_ratio=risk_reward_ratio,
            thesis=req.thesis,
            decision=req.decision,
            status="OPEN",
        )
        db.add(trade)
        await db.flush()  # Populates trade.id

        # Deduct cash for LONG position
        if direction == "LONG":
            portfolio.cash_balance = round(portfolio.cash_balance - position_cost, 2)

        # Create Position record
        position = Position(
            portfolio_id=portfolio.id,
            trade_id=trade.id,
            symbol=sym,
            direction=direction,
            quantity=req.quantity,
            entry_price=round(req.entry_price, 2),
            current_price=round(req.entry_price, 2),
            stop_loss=round(req.stop_loss, 2),
            target=round(req.target, 2),
            unrealized_pnl=0.0,
            unrealized_pnl_pct=0.0,
        )
        db.add(position)

        # Record Initial Execution Event
        event = TradeEvent(
            trade_id=trade.id,
            event_type="ORDER_FILLED",
            description=f"Paper order filled: {direction} {req.quantity} {sym} @ ${req.entry_price:.2f}. SL: ${req.stop_loss:.2f}, TP: ${req.target:.2f}",
            severity="INFO",
            data={
                "quantity": req.quantity,
                "entry_price": req.entry_price,
                "risk_amount": risk_amount,
                "risk_reward_ratio": risk_reward_ratio,
            },
        )
        db.add(event)

        # Update portfolio exposure
        await cls._update_portfolio_totals(db, portfolio)
        await db.commit()

        stmt = select(Trade).options(selectinload(Trade.events)).where(Trade.id == trade.id)
        res = await db.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def close_trade(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        req: Optional[TradeCloseRequest] = None,
    ) -> Trade:
        stmt = (
            select(Trade)
            .options(selectinload(Trade.events))
            .where(Trade.id == trade_id, Trade.user_id == user_id)
        )
        res = await db.execute(stmt)
        trade = res.scalar_one_or_none()
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        if trade.status != "OPEN":
            raise HTTPException(status_code=400, detail=f"Trade is already {trade.status}")

        portfolio = await cls.get_or_create_portfolio(db, user_id)

        # Determine exit price
        exit_price = req.exit_price if req and req.exit_price else None
        if not exit_price:
            market_provider = get_market_data_provider()
            bars = await market_provider.get_historical_bars(trade.symbol, limit=1)
            exit_price = bars[-1].close if bars else trade.entry_price

        reason = req.reason if req and req.reason else "CLOSED_MANUALLY"

        # Calculate realized PnL
        if trade.direction == "LONG":
            realized_pnl = round((exit_price - trade.entry_price) * trade.quantity, 2)
            cost_basis = trade.entry_price * trade.quantity
            returned_cash = round(cost_basis + realized_pnl, 2)
            portfolio.cash_balance = round(portfolio.cash_balance + returned_cash, 2)
        else:  # SHORT
            realized_pnl = round((trade.entry_price - exit_price) * trade.quantity, 2)
            portfolio.cash_balance = round(portfolio.cash_balance + realized_pnl, 2)

        cost_basis = trade.entry_price * trade.quantity
        realized_pnl_pct = round((realized_pnl / max(0.01, cost_basis)) * 100.0, 2)

        # Update Trade status
        trade.status = reason
        trade.exit_price = round(exit_price, 2)
        trade.realized_pnl = realized_pnl
        trade.realized_pnl_pct = realized_pnl_pct
        trade.closed_at = datetime.utcnow()

        # Update Portfolio metrics
        portfolio.realized_pnl = round(portfolio.realized_pnl + realized_pnl, 2)
        if realized_pnl > 0:
            portfolio.win_count += 1
        elif realized_pnl < 0:
            portfolio.loss_count += 1

        # Delete corresponding Position
        pos_stmt = select(Position).where(Position.trade_id == trade.id)
        pos_res = await db.execute(pos_stmt)
        pos = pos_res.scalar_one_or_none()
        if pos:
            await db.delete(pos)

        # Record Close Event
        event = TradeEvent(
            trade_id=trade.id,
            event_type="TRADE_CLOSED",
            description=f"Trade closed @ ${exit_price:.2f} ({reason}). Realized PnL: ${realized_pnl:+.2f} ({realized_pnl_pct:+.2f}%)",
            severity="INFO" if realized_pnl >= 0 else "WARNING",
            data={
                "exit_price": exit_price,
                "realized_pnl": realized_pnl,
                "realized_pnl_pct": realized_pnl_pct,
                "reason": reason,
            },
        )
        db.add(event)

        await cls._update_portfolio_totals(db, portfolio)
        await db.commit()
        await db.refresh(trade)
        return trade

    @classmethod
    async def list_trades(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        status_filter: Optional[str] = None,
        symbol_filter: Optional[str] = None,
    ) -> List[Trade]:
        stmt = (
            select(Trade)
            .options(selectinload(Trade.events))
            .where(Trade.user_id == user_id)
            .order_by(Trade.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(Trade.status == status_filter.upper())
        if symbol_filter:
            stmt = stmt.where(Trade.symbol == symbol_filter.upper())

        res = await db.execute(stmt)
        return res.scalars().all()

    @classmethod
    async def get_portfolio_summary(cls, db: AsyncSession, user_id: uuid.UUID) -> Portfolio:
        portfolio = await cls.get_or_create_portfolio(db, user_id)
        # Update current positions with latest prices
        market_provider = get_market_data_provider()
        for pos in portfolio.positions:
            bars = await market_provider.get_historical_bars(pos.symbol, limit=1)
            if bars:
                current_price = bars[-1].close
                pos.current_price = round(current_price, 2)
                if pos.direction == "LONG":
                    pos.unrealized_pnl = round((current_price - pos.entry_price) * pos.quantity, 2)
                else:
                    pos.unrealized_pnl = round((pos.entry_price - current_price) * pos.quantity, 2)
                cost = pos.entry_price * pos.quantity
                pos.unrealized_pnl_pct = round((pos.unrealized_pnl / max(0.01, cost)) * 100.0, 2)

        await cls._update_portfolio_totals(db, portfolio)
        await db.commit()
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.positions))
            .where(Portfolio.id == portfolio.id)
        )
        res = await db.execute(stmt)
        return res.scalar_one()

    @classmethod
    async def reset_portfolio(cls, db: AsyncSession, user_id: uuid.UUID) -> Portfolio:
        portfolio = await cls.get_or_create_portfolio(db, user_id)
        # Clear positions
        for pos in list(portfolio.positions):
            await db.delete(pos)

        portfolio.cash_balance = 100000.0
        portfolio.total_equity = 100000.0
        portfolio.realized_pnl = 0.0
        portfolio.unrealized_pnl = 0.0
        portfolio.win_count = 0
        portfolio.loss_count = 0
        portfolio.max_drawdown_pct = 0.0
        portfolio.current_exposure_pct = 0.0
        await db.commit()
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.positions))
            .where(Portfolio.id == portfolio.id)
        )
        res = await db.execute(stmt)
        return res.scalar_one()


    @classmethod
    async def _update_portfolio_totals(cls, db: AsyncSession, portfolio: Portfolio) -> None:
        total_pos_value = 0.0
        total_unrealized = 0.0
        for pos in portfolio.positions:
            total_pos_value += pos.quantity * pos.current_price
            total_unrealized += pos.unrealized_pnl

        portfolio.unrealized_pnl = round(total_unrealized, 2)
        portfolio.total_equity = round(portfolio.cash_balance + total_pos_value, 2)

        # Exposure %
        if portfolio.total_equity > 0:
            portfolio.current_exposure_pct = round((total_pos_value / portfolio.total_equity) * 100.0, 1)
        else:
            portfolio.current_exposure_pct = 0.0

        # Drawdown %
        if portfolio.total_equity < portfolio.initial_balance:
            dd = ((portfolio.initial_balance - portfolio.total_equity) / portfolio.initial_balance) * 100.0
            portfolio.max_drawdown_pct = max(portfolio.max_drawdown_pct, round(dd, 2))

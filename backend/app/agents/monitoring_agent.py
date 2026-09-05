import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.trade import Trade, TradeEvent
from app.models.alert import Alert
from app.services.market_data.factory import get_market_data_provider
from app.services.trading.paper_engine import PaperTradingEngine
from app.schemas.trade import TradeCloseRequest


class MonitoringAgent:
    """
    Automated Trade Monitoring Agent:
    Tracks open paper positions in real-time, validates stops & targets,
    executes automated paper closes on invalidations, and issues alerts.
    """

    @classmethod
    async def check_open_trades(
        cls, db: AsyncSession, user_id: Optional[uuid.UUID] = None
    ) -> dict:
        stmt = (
            select(Trade)
            .options(selectinload(Trade.events))
            .where(Trade.status == "OPEN")
        )
        if user_id:
            stmt = stmt.where(Trade.user_id == user_id)

        res = await db.execute(stmt)
        open_trades = res.scalars().all()

        checked_count = len(open_trades)
        triggered_events = 0
        alerts_created = 0
        details: List[str] = []

        market_provider = get_market_data_provider()

        for trade in open_trades:
            bars = await market_provider.get_historical_bars(trade.symbol, limit=1)
            if not bars:
                continue

            current_price = bars[-1].close
            direction = trade.direction.upper()

            # 1. Stop Loss Check
            stop_hit = False
            if direction == "LONG" and current_price <= trade.stop_loss:
                stop_hit = True
            elif direction == "SHORT" and current_price >= trade.stop_loss:
                stop_hit = True

            if stop_hit:
                # Close trade via PaperTradingEngine
                close_req = TradeCloseRequest(
                    exit_price=trade.stop_loss,
                    reason="STOP_HIT",
                )
                await PaperTradingEngine.close_trade(
                    db=db, user_id=trade.user_id, trade_id=trade.id, req=close_req
                )
                # Create Alert
                alert = Alert(
                    user_id=trade.user_id,
                    trade_id=trade.id,
                    symbol=trade.symbol,
                    alert_type="STOP_LOSS_HIT",
                    title=f"Stop Loss Triggered for {trade.symbol}",
                    message=f"Paper stop loss executed at ${trade.stop_loss:.2f}. Capital preserved according to risk plan.",
                    severity="WARNING",
                    data={"exit_price": trade.stop_loss, "direction": trade.direction},
                )
                db.add(alert)
                triggered_events += 1
                alerts_created += 1
                details.append(f"Auto-closed {trade.symbol} (Stop Loss hit @ ${trade.stop_loss:.2f})")
                continue

            # 2. Target Hit Check
            target_hit = False
            if direction == "LONG" and current_price >= trade.target:
                target_hit = True
            elif direction == "SHORT" and current_price <= trade.target:
                target_hit = True

            if target_hit:
                close_req = TradeCloseRequest(
                    exit_price=trade.target,
                    reason="TARGET_HIT",
                )
                await PaperTradingEngine.close_trade(
                    db=db, user_id=trade.user_id, trade_id=trade.id, req=close_req
                )
                alert = Alert(
                    user_id=trade.user_id,
                    trade_id=trade.id,
                    symbol=trade.symbol,
                    alert_type="TARGET_HIT",
                    title=f"Take-Profit Target Achieved for {trade.symbol}",
                    message=f"Paper target hit at ${trade.target:.2f}. Planned profit locked in.",
                    severity="INFO",
                    data={"exit_price": trade.target, "direction": trade.direction},
                )
                db.add(alert)
                triggered_events += 1
                alerts_created += 1
                details.append(f"Auto-closed {trade.symbol} (Target hit @ ${trade.target:.2f})")
                continue

            # 3. Regular Periodic Status Log
            pnl = (
                (current_price - trade.entry_price) * trade.quantity
                if direction == "LONG"
                else (trade.entry_price - current_price) * trade.quantity
            )
            event = TradeEvent(
                trade_id=trade.id,
                event_type="PRICE_MONITOR",
                description=f"Price check: ${current_price:.2f}. Unrealized PnL: ${pnl:+.2f}",
                severity="INFO",
                data={"current_price": current_price, "unrealized_pnl": pnl},
            )
            db.add(event)
            triggered_events += 1

        await db.commit()

        return {
            "checked_trades_count": checked_count,
            "triggered_events_count": triggered_events,
            "alerts_created_count": alerts_created,
            "details": details,
        }

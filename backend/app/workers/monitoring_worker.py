import asyncio
import logging
from app.core.config import settings
from app.db.session import AsyncSessionFactory
from app.agents.monitoring_agent import MonitoringAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TradeTraceMonitoringWorker")


async def run_monitoring_loop():
    """
    Background worker periodically evaluating active paper positions against
    market prices, stop losses, and target levels.
    """
    logger.info(
        f"Starting TradeTrace Monitoring Worker (Polling interval: {settings.MONITORING_INTERVAL_SECONDS}s)"
    )
    while True:
        try:
            async with AsyncSessionFactory() as db:
                res = await MonitoringAgent.check_open_trades(db)
                if res["checked_trades_count"] > 0:
                    logger.info(
                        f"Monitored {res['checked_trades_count']} trades | Events: {res['triggered_events_count']} | Alerts: {res['alerts_created_count']}"
                    )
        except Exception as e:
            logger.error(f"Error during monitoring loop check: {e}")

        await asyncio.sleep(settings.MONITORING_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(run_monitoring_loop())
    except KeyboardInterrupt:
        logger.info("Monitoring worker stopped by user.")

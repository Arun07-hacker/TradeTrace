import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.tools.base import ToolResult, log_tool_execution
from app.models.alert import Alert


@log_tool_execution("alert.create_alert")
async def create_alert(
    db: AsyncSession,
    user_id: uuid.UUID,
    symbol: str,
    alert_type: str,
    title: str,
    message: str,
    severity: str = "INFO",
    trade_id: Optional[uuid.UUID] = None,
) -> ToolResult:
    """Create a new alert notification for the user."""
    try:
        alert = Alert(
            user_id=user_id,
            trade_id=trade_id,
            symbol=symbol,
            alert_type=alert_type,
            title=title,
            message=message,
            severity=severity,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return ToolResult(
            tool="alert.create_alert",
            status="success",
            data={
                "alert_id": str(alert.id),
                "alert_type": alert.alert_type,
                "title": alert.title,
                "severity": alert.severity,
            },
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="alert.create_alert",
            status="error",
            data=None,
            error=str(e),
        )


@log_tool_execution("alert.get_alerts")
async def get_alerts(
    db: AsyncSession,
    user_id: uuid.UUID,
    unread_only: bool = False,
) -> ToolResult:
    """Retrieve alerts for a user, optionally filtering to unread only."""
    try:
        stmt = (
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
        )
        if unread_only:
            stmt = stmt.where(Alert.is_read == False)  # noqa: E712

        result = await db.execute(stmt)
        alerts = result.scalars().all()
        alerts_data = []
        for a in alerts:
            alerts_data.append({
                "id": str(a.id),
                "symbol": a.symbol,
                "alert_type": a.alert_type,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "is_read": a.is_read,
                "created_at": str(a.created_at),
            })
        return ToolResult(
            tool="alert.get_alerts",
            status="success",
            data=alerts_data,
            error=None,
        )
    except Exception as e:
        return ToolResult(
            tool="alert.get_alerts",
            status="error",
            data=None,
            error=str(e),
        )

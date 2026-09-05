import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, MonitoringCheckResponse
from app.agents.monitoring_agent import MonitoringAgent

router = APIRouter(tags=["Monitoring & Alerts"])


@router.post("/monitoring/check-now", response_model=MonitoringCheckResponse)
async def run_monitoring_check(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual position check across all open paper trades."""
    res = await MonitoringAgent.check_open_trades(db=db, user_id=current_user.id)
    return MonitoringCheckResponse(
        checked_trades_count=res["checked_trades_count"],
        triggered_events_count=res["triggered_events_count"],
        alerts_created_count=res["alerts_created_count"],
        details=res["details"],
    )


@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all monitoring alerts and notifications for current user."""
    stmt = (
        select(Alert)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/alerts/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_read(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a specific alert as read."""
    stmt = select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id)
    res = await db.execute(stmt)
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/alerts/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_alerts_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all active notifications and alerts as read."""
    stmt = update(Alert).where(Alert.user_id == current_user.id).values(is_read=True)
    await db.execute(stmt)
    await db.commit()
    return {"status": "ok", "message": "All alerts marked as read."}

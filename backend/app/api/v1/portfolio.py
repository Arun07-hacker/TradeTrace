from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.trade import PortfolioResponse
from app.services.trading import PaperTradingEngine

router = APIRouter(prefix="/portfolio", tags=["Paper Portfolio Management"])


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve current paper trading portfolio summary, total equity, cash, and open positions."""
    return await PaperTradingEngine.get_portfolio_summary(db=db, user_id=current_user.id)


@router.post("/reset", response_model=PortfolioResponse)
async def reset_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset paper trading portfolio balance back to initial $100,000 cash balance."""
    return await PaperTradingEngine.reset_portfolio(db=db, user_id=current_user.id)

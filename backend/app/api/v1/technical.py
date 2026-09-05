from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.technical import TechnicalAnalysisResult
from app.services.market_data.factory import get_market_data_provider
from app.services.market_data.base import MarketDataProvider
from app.analysis.engine import TechnicalAnalysisEngine

router = APIRouter(prefix="/technical", tags=["Technical Analysis Engine"])


@router.get("/{symbol}", response_model=TechnicalAnalysisResult)
async def get_technical_analysis(
    symbol: str,
    timeframe: str = Query("1d", pattern="^(1h|4h|1d|1w)$", description="Candlestick timeframe"),
    limit: int = Query(100, ge=30, le=300, description="Number of bars to calculate indicators over"),
    market_provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """
    Deterministic Technical Analysis Engine endpoint.
    Calculates SMA (20, 50, 200), EMA (12, 26), RSI (14), MACD (12,26,9),
    ATR (14), annualized volatility %, volume analysis, support/resistance pivots,
    and algorithmic trend detection without LLM guessing.
    """
    sym = symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")

    bars = await market_provider.get_historical_bars(sym, timeframe=timeframe, limit=limit)
    if not bars:
        raise HTTPException(status_code=404, detail=f"No market data available for {sym}")

    result = TechnicalAnalysisEngine.analyze(sym, bars, is_demo=True)
    return result

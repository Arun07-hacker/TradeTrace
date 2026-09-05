from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.market import MarketQuote, HistoricalDataResponse, SymbolInfo
from app.services.market_data.factory import get_market_data_provider
from app.services.market_data.base import MarketDataProvider

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/symbols", response_model=List[SymbolInfo])
async def list_symbols(
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """List supported watchlist symbols with current overview pricing."""
    return await provider.get_supported_symbols()


@router.get("/{symbol}", response_model=MarketQuote)
async def get_quote(
    symbol: str,
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve latest quote, session change, and volume for a symbol."""
    sym = symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")
    return await provider.get_latest_quote(sym)


@router.get("/{symbol}/history", response_model=HistoricalDataResponse)
async def get_history(
    symbol: str,
    timeframe: str = Query("1d", pattern="^(1h|4h|1d|1w)$", description="Candle timeframe"),
    limit: int = Query(100, ge=10, le=500, description="Number of bars to retrieve"),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """Fetch historical OHLCV candlestick bars for technical analysis and charting."""
    sym = symbol.upper().strip()
    if not sym:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")

    bars = await provider.get_historical_bars(sym, timeframe=timeframe, limit=limit)
    return HistoricalDataResponse(
        symbol=sym,
        timeframe=timeframe,
        count=len(bars),
        bars=bars,
        is_demo=True,
    )

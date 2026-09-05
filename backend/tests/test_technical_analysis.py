import pytest
import pandas as pd
import numpy as np
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.market import OHLCVBar
from app.services.market_data.mock_provider import MockMarketDataProvider
from app.analysis.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_atr,
    calculate_volatility,
    detect_support_resistance,
    detect_trend,
    analyze_volume,
)
from app.analysis.engine import TechnicalAnalysisEngine


@pytest.fixture
def mock_bars():
    provider = MockMarketDataProvider(seed=42)
    import asyncio
    return asyncio.run(provider.get_historical_bars("AAPL", timeframe="1d", limit=100))


@pytest.fixture
async def api_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def test_sma_calculation():
    """Verify deterministic SMA calculation against known math."""
    data = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    sma_3 = calculate_sma(data, 3)
    assert round(sma_3.iloc[-1], 2) == 40.0  # (30 + 40 + 50) / 3
    assert round(sma_3.iloc[-2], 2) == 30.0  # (20 + 30 + 40) / 3


def test_ema_calculation():
    """Verify EMA responds more heavily to the most recent price."""
    data = pd.Series([10.0, 10.0, 10.0, 10.0, 20.0])
    sma_5 = calculate_sma(data, 5).iloc[-1]
    ema_5 = calculate_ema(data, 5).iloc[-1]
    # EMA must be higher than SMA when the last price jumped
    assert ema_5 > sma_5


def test_rsi_calculation_and_bounds():
    """Verify RSI boundaries and sensitivity."""
    # Strongly bullish series
    up_series = pd.Series([100.0 + i * 2.0 for i in range(30)])
    rsi_up = calculate_rsi(up_series, 14)
    assert rsi_up > 80.0
    assert rsi_up <= 100.0

    # Strongly bearish series
    down_series = pd.Series([200.0 - i * 2.0 for i in range(30)])
    rsi_down = calculate_rsi(down_series, 14)
    assert rsi_down < 20.0
    assert rsi_down >= 0.0


def test_macd_calculation():
    """Verify MACD output format and histogram math."""
    series = pd.Series(np.linspace(100, 150, 50))
    macd_res = calculate_macd(series, fast=12, slow=26, signal_period=9)
    assert "macd" in macd_res
    assert "signal" in macd_res
    assert "histogram" in macd_res
    # Rising prices should produce positive MACD line
    assert macd_res["macd"] > 0


def test_atr_calculation():
    """Verify ATR measurement of true range."""
    high = pd.Series([105.0, 107.0, 110.0, 108.0, 112.0] * 5)
    low = pd.Series([98.0, 100.0, 102.0, 101.0, 105.0] * 5)
    close = pd.Series([102.0, 104.0, 106.0, 104.0, 109.0] * 5)
    atr = calculate_atr(high, low, close, 14)
    assert atr > 0.0
    assert atr < 20.0


def test_volatility_calculation():
    """Verify historical annualized volatility."""
    close = pd.Series([100.0 * (1.0 + 0.01 * ((-1) ** i)) for i in range(40)])
    vol = calculate_volatility(close, 20)
    assert vol > 0.0
    assert vol < 100.0


def test_support_resistance_detection():
    """Verify detected key support is below current price and resistance is above."""
    current_price = 220.0
    high = pd.Series([215.0, 222.0, 228.0, 224.0, 230.0, 225.0, 221.0] * 5)
    low = pd.Series([210.0, 216.0, 218.0, 215.0, 219.0, 214.0, 212.0] * 5)
    close = pd.Series([214.0, 220.0, 225.0, 220.0, 226.0, 222.0, current_price] * 5)

    sr = detect_support_resistance(high, low, close, current_price)
    assert sr["key_support"] <= current_price
    assert sr["key_resistance"] >= current_price
    assert len(sr["support_levels"]) > 0
    assert len(sr["resistance_levels"]) > 0


def test_trend_detection():
    """Verify trend direction determination."""
    bullish = detect_trend(
        current_price=230.0,
        sma_20=220.0,
        sma_50=210.0,
        sma_200=190.0,
        rsi=65.0,
        macd_hist=1.5,
    )
    assert bullish["trend"] == "bullish"
    assert bullish["strength"] >= 0.7

    bearish = detect_trend(
        current_price=180.0,
        sma_20=190.0,
        sma_50=200.0,
        sma_200=210.0,
        rsi=35.0,
        macd_hist=-1.2,
    )
    assert bearish["trend"] == "bearish"
    assert bearish["strength"] >= 0.7


def test_volume_analysis():
    """Verify volume signals."""
    vol_series = pd.Series([1000000] * 19 + [2500000])
    vol_data = analyze_volume(vol_series, 20)
    assert vol_data["volume_signal"] == "above_average"
    assert vol_data["volume_ratio"] > 1.25


def test_technical_analysis_engine_end_to_end(mock_bars):
    """Verify TechnicalAnalysisEngine full execution on bars."""
    res = TechnicalAnalysisEngine.analyze("AAPL", mock_bars)
    assert res.symbol == "AAPL"
    assert res.current_price > 0
    assert res.trend in ["bullish", "bearish", "neutral"]
    assert 0.0 <= res.rsi <= 100.0
    assert res.sma_20 > 0
    assert res.sma_50 > 0
    assert res.atr > 0
    assert res.volume_signal in ["above_average", "below_average", "average"]
    assert res.support_resistance.key_support <= res.current_price
    assert res.support_resistance.key_resistance >= res.current_price


@pytest.mark.asyncio
async def test_api_technical_endpoint(api_client: AsyncClient):
    """Test REST API GET /api/v1/technical/AAPL."""
    response = await api_client.get("/api/v1/technical/AAPL")
    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "AAPL"
    assert "trend" in data
    assert "rsi" in data
    assert "sma_20" in data
    assert "sma_50" in data
    assert "atr" in data
    assert "volume_signal" in data
    assert data["is_demo"] is True

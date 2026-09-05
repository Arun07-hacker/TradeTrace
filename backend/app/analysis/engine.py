from datetime import datetime, timezone
from typing import List, Union
import pandas as pd

from app.schemas.market import OHLCVBar
from app.schemas.technical import (
    TechnicalAnalysisResult,
    MACDData,
    TrendData,
    VolumeData,
    SupportResistanceLevels,
)
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


class TechnicalAnalysisEngine:
    """
    Deterministic Technical Analysis Calculation Engine.
    Processes OHLCV time series data with pure mathematics (Zero LLM hallucinations).
    """

    @classmethod
    def analyze(cls, symbol: str, bars: List[OHLCVBar], is_demo: bool = True) -> TechnicalAnalysisResult:
        if not bars:
            raise ValueError(f"No OHLCV bars provided for {symbol}")

        # Convert to DataFrame
        records = [b.model_dump() if hasattr(b, "model_dump") else dict(b) for b in bars]
        df = pd.DataFrame(records)
        df.sort_values(by="timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]
        current_price = round(float(close.iloc[-1]), 2)

        # 1. Moving Averages
        sma_20_series = calculate_sma(close, 20)
        sma_50_series = calculate_sma(close, 50)
        sma_20 = round(float(sma_20_series.iloc[-1]), 2)
        sma_50 = round(float(sma_50_series.iloc[-1]), 2)

        sma_200 = None
        if len(close) >= 180:
            sma_200_series = calculate_sma(close, 200)
            sma_200 = round(float(sma_200_series.iloc[-1]), 2)

        ema_12_series = calculate_ema(close, 12)
        ema_26_series = calculate_ema(close, 26)
        ema_12 = round(float(ema_12_series.iloc[-1]), 2)
        ema_26 = round(float(ema_26_series.iloc[-1]), 2)

        # 2. RSI (14)
        rsi = calculate_rsi(close, 14)

        # 3. MACD (12, 26, 9)
        macd_dict = calculate_macd(close, 12, 26, 9)
        macd_data = MACDData(
            macd=macd_dict["macd"],
            signal=macd_dict["signal"],
            histogram=macd_dict["histogram"],
        )

        # 4. ATR (14)
        atr = calculate_atr(high, low, close, 14)

        # 5. Volatility (20-day annualized)
        volatility_pct = calculate_volatility(close, 20)

        # 6. Trend Detection
        trend_dict = detect_trend(
            current_price=current_price,
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            rsi=rsi,
            macd_hist=macd_data.histogram,
        )
        trend_data = TrendData(
            trend=trend_dict["trend"],
            strength=trend_dict["strength"],
            description=trend_dict["description"],
        )

        # 7. Volume Analysis
        vol_dict = analyze_volume(volume, 20)
        volume_data = VolumeData(
            volume_signal=vol_dict["volume_signal"],
            current_volume=vol_dict["current_volume"],
            avg_volume_20=vol_dict["avg_volume_20"],
            volume_ratio=vol_dict["volume_ratio"],
        )

        # 8. Support and Resistance
        sr_dict = detect_support_resistance(high, low, close, current_price)
        sr_data = SupportResistanceLevels(
            support_levels=sr_dict["support_levels"],
            resistance_levels=sr_dict["resistance_levels"],
            key_support=sr_dict["key_support"],
            key_resistance=sr_dict["key_resistance"],
        )

        return TechnicalAnalysisResult(
            symbol=symbol.upper(),
            current_price=current_price,
            trend=trend_data.trend,
            trend_details=trend_data,
            rsi=rsi,
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            ema_12=ema_12,
            ema_26=ema_26,
            macd=macd_data,
            atr=atr,
            volatility_pct=volatility_pct,
            volume_signal=volume_data.volume_signal,
            volume_details=volume_data,
            support_resistance=sr_data,
            generated_at=datetime.now(timezone.utc),
            is_demo=is_demo,
        )

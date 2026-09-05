from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MACDData(BaseModel):
    macd: float = Field(..., description="MACD fast-slow difference line")
    signal: float = Field(..., description="Signal line (9-period EMA of MACD)")
    histogram: float = Field(..., description="MACD histogram")


class TrendData(BaseModel):
    trend: str = Field(..., description="Overall trend ('bullish', 'bearish', or 'neutral')")
    strength: float = Field(..., ge=0.0, le=1.0, description="Trend strength score from 0.0 to 1.0")
    description: str = Field(..., description="Human-readable trend explanation")


class VolumeData(BaseModel):
    volume_signal: str = Field(..., description="'above_average', 'below_average', or 'average'")
    current_volume: int = Field(..., description="Latest bar trading volume")
    avg_volume_20: int = Field(..., description="20-period average volume")
    volume_ratio: float = Field(..., description="Current volume relative to 20-period SMA")


class SupportResistanceLevels(BaseModel):
    support_levels: List[float] = Field(..., description="Identified horizontal support price clusters")
    resistance_levels: List[float] = Field(..., description="Identified horizontal resistance price clusters")
    key_support: float = Field(..., description="Nearest key support level below current price")
    key_resistance: float = Field(..., description="Nearest key resistance level above current price")


class TechnicalAnalysisResult(BaseModel):
    symbol: str = Field(..., description="Ticker symbol")
    current_price: float = Field(..., description="Latest traded close price")
    trend: str = Field(..., description="Trend direction: bullish, bearish, or neutral")
    trend_details: TrendData = Field(..., description="Comprehensive trend analysis")
    rsi: float = Field(..., ge=0.0, le=100.0, description="Relative Strength Index (14-period Wilder's)")
    sma_20: float = Field(..., description="20-period Simple Moving Average")
    sma_50: float = Field(..., description="50-period Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-period Simple Moving Average if available")
    ema_12: float = Field(..., description="12-period Exponential Moving Average")
    ema_26: float = Field(..., description="26-period Exponential Moving Average")
    macd: MACDData = Field(..., description="MACD indicator components")
    atr: float = Field(..., description="Average True Range (14-period)")
    volatility_pct: float = Field(..., description="Annualized historical volatility percentage")
    volume_signal: str = Field(..., description="Volume behavior signal")
    volume_details: VolumeData = Field(..., description="Detailed volume statistics")
    support_resistance: SupportResistanceLevels = Field(..., description="Support and resistance levels")
    generated_at: datetime = Field(..., description="Analysis UTC timestamp")
    is_demo: bool = Field(True, description="True if based on demo market data")

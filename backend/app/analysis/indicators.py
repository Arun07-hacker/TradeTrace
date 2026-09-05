import math
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return series.rolling(window=period, min_periods=1).mean()


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """
    Calculate Wilder's Relative Strength Index (RSI).
    Bounded strictly between 0.0 and 100.0.
    """
    if len(series) < period + 1:
        return 50.0

    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing (alpha = 1 / period)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    latest_gain = avg_gain.iloc[-1]
    latest_loss = avg_loss.iloc[-1]

    if latest_loss == 0 or np.isnan(latest_loss):
        return 100.0 if latest_gain > 0 else 50.0
    if latest_gain == 0 or np.isnan(latest_gain):
        return 0.0

    rs = latest_gain / latest_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return round(float(np.clip(rsi, 0.0, 100.0)), 1)


def calculate_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> Dict[str, float]:
    """
    Calculate Moving Average Convergence Divergence (MACD).
    Returns macd, signal, and histogram.
    """
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    return {
        "macd": round(float(macd_line.iloc[-1]), 2),
        "signal": round(float(signal_line.iloc[-1]), 2),
        "histogram": round(float(histogram.iloc[-1]), 2),
    }


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> float:
    """
    Calculate Average True Range (ATR).
    TR = max[(high - low), abs(high - close_prev), abs(low - close_prev)]
    """
    if len(close) < 2:
        return round(float(high.iloc[-1] - low.iloc[-1]), 2)

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    val = atr.iloc[-1] if not np.isnan(atr.iloc[-1]) else true_range.mean()
    return round(float(val), 2)


def calculate_volatility(close: pd.Series, period: int = 20) -> float:
    """
    Calculate annualized historical volatility percentage.
    volatility = std(daily_returns) * sqrt(252) * 100
    """
    if len(close) < 2:
        return 15.0

    returns = close.pct_change().dropna()
    rolling_returns = returns.tail(period)
    if len(rolling_returns) < 2:
        return 15.0

    daily_std = rolling_returns.std()
    annualized_vol = daily_std * math.sqrt(252) * 100.0
    return round(float(annualized_vol), 1)


def detect_support_resistance(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    current_price: float,
    window: int = 5,
) -> Dict[str, Any]:
    """
    Identify key horizontal support and resistance pivot levels from swing highs/lows.
    """
    pivot_highs: List[float] = []
    pivot_lows: List[float] = []

    # Swing high: higher than 'window' bars left and right
    for i in range(window, len(high) - window):
        is_high = all(high.iloc[i] >= high.iloc[i - j] for j in range(1, window + 1)) and \
                  all(high.iloc[i] >= high.iloc[i + j] for j in range(1, window + 1))
        if is_high:
            pivot_highs.append(round(float(high.iloc[i]), 2))

        is_low = all(low.iloc[i] <= low.iloc[i - j] for j in range(1, window + 1)) and \
                 all(low.iloc[i] <= low.iloc[i + j] for j in range(1, window + 1))
        if is_low:
            pivot_lows.append(round(float(low.iloc[i]), 2))

    # Cluster nearby levels within 1.0% tolerance
    def cluster_levels(levels: List[float]) -> List[float]:
        if not levels:
            return []
        sorted_lvls = sorted(levels)
        clusters: List[float] = []
        cur_cluster = [sorted_lvls[0]]
        for val in sorted_lvls[1:]:
            if (val - cur_cluster[-1]) / cur_cluster[-1] <= 0.015:
                cur_cluster.append(val)
            else:
                clusters.append(round(float(np.mean(cur_cluster)), 2))
                cur_cluster = [val]
        clusters.append(round(float(np.mean(cur_cluster)), 2))
        return clusters

    clean_resistances = [r for r in cluster_levels(pivot_highs) if r > current_price]
    clean_supports = [s for s in cluster_levels(pivot_lows) if s < current_price]

    # Fallback if no swing pivots detected
    recent_min = round(float(low.tail(20).min()), 2)
    recent_max = round(float(high.tail(20).max()), 2)

    if not clean_supports:
        clean_supports = [round(min(current_price * 0.96, recent_min), 2)]
    if not clean_resistances:
        clean_resistances = [round(max(current_price * 1.04, recent_max), 2)]

    key_support = max(clean_supports)
    key_resistance = min(clean_resistances)

    return {
        "support_levels": clean_supports[:4],
        "resistance_levels": clean_resistances[:4],
        "key_support": key_support,
        "key_resistance": key_resistance,
    }


def detect_trend(
    current_price: float,
    sma_20: float,
    sma_50: float,
    sma_200: Optional[float],
    rsi: float,
    macd_hist: float,
) -> Dict[str, Any]:
    """
    Determine deterministic trend direction and strength score (0.0 to 1.0).
    """
    bull_points = 0
    bear_points = 0
    total_points = 5

    # 1. Price vs SMA 20
    if current_price > sma_20:
        bull_points += 1
    else:
        bear_points += 1

    # 2. SMA 20 vs SMA 50
    if sma_20 > sma_50:
        bull_points += 1
    else:
        bear_points += 1

    # 3. SMA 200 comparison if available
    if sma_200 is not None:
        total_points += 1
        if current_price > sma_200:
            bull_points += 1
        else:
            bear_points += 1

    # 4. RSI momentum
    if rsi > 55:
        bull_points += 1
    elif rsi < 45:
        bear_points += 1

    # 5. MACD histogram
    if macd_hist > 0:
        bull_points += 1
    elif macd_hist < 0:
        bear_points += 1

    net_score = (bull_points - bear_points) / total_points

    if net_score >= 0.3:
        trend = "bullish"
        strength = round(min(1.0, 0.5 + net_score * 0.5), 2)
        desc = f"Upward momentum with price above SMA-20 (${sma_20}) and positive MACD histogram."
    elif net_score <= -0.3:
        trend = "bearish"
        strength = round(min(1.0, 0.5 + abs(net_score) * 0.5), 2)
        desc = f"Downward momentum with price below SMA-20 (${sma_20}) and negative MACD histogram."
    else:
        trend = "neutral"
        strength = round(1.0 - abs(net_score), 2)
        desc = f"Consolidating market action around SMA-20 (${sma_20}) with balanced momentum."

    return {
        "trend": trend,
        "strength": strength,
        "description": desc,
    }


def analyze_volume(volume_series: pd.Series, period: int = 20) -> Dict[str, Any]:
    """
    Compare current volume to its 20-period moving average.
    """
    if len(volume_series) == 0:
        return {
            "volume_signal": "average",
            "current_volume": 0,
            "avg_volume_20": 0,
            "volume_ratio": 1.0,
        }

    current_vol = int(volume_series.iloc[-1])
    avg_vol = int(volume_series.tail(period).mean())
    ratio = round(current_vol / avg_vol, 2) if avg_vol > 0 else 1.0

    if ratio >= 1.25:
        signal = "above_average"
    elif ratio <= 0.75:
        signal = "below_average"
    else:
        signal = "average"

    return {
        "volume_signal": signal,
        "current_volume": current_vol,
        "avg_volume_20": avg_vol,
        "volume_ratio": ratio,
    }

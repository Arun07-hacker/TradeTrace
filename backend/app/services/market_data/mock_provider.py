import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from app.services.market_data.base import MarketDataProvider
from app.schemas.market import MarketQuote, OHLCVBar, SymbolInfo

# Base asset metadata and reference parameters
SUPPORTED_ASSETS: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "base_price": 224.50,
        "daily_volatility": 0.015,
        "avg_volume": 52000000,
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "base_price": 448.20,
        "daily_volatility": 0.014,
        "avg_volume": 24000000,
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "base_price": 126.80,
        "daily_volatility": 0.028,
        "avg_volume": 68000000,
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "exchange": "NASDAQ",
        "asset_class": "EQUITY",
        "base_price": 248.60,
        "daily_volatility": 0.035,
        "avg_volume": 85000000,
    },
}


class MockMarketDataProvider(MarketDataProvider):
    """
    Realistic simulated market data provider for offline/demo development.
    Uses seeded stochastic drift to produce consistent, realistic OHLCV bars.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed

    def _get_asset_params(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        if sym in SUPPORTED_ASSETS:
            return SUPPORTED_ASSETS[sym]
        # Generic fallback for unlisted symbols
        return {
            "name": f"{sym} Corporation",
            "exchange": "NYSE",
            "asset_class": "EQUITY",
            "base_price": 100.0,
            "daily_volatility": 0.02,
            "avg_volume": 10000000,
        }

    async def get_latest_quote(self, symbol: str) -> MarketQuote:
        sym = symbol.upper().strip()
        params = self._get_asset_params(sym)
        base = params["base_price"]
        vol = params["daily_volatility"]

        # Predictable pseudo-random variation based on current minute
        now = datetime.now(timezone.utc)
        minute_hash = (now.minute + now.hour * 60) / 1440.0
        drift = math.sin(minute_hash * math.pi * 2) * vol * 0.5
        current_price = round(base * (1.0 + drift), 2)
        open_price = round(base, 2)
        change = round(current_price - open_price, 2)
        change_pct = round((change / open_price) * 100, 2) if open_price > 0 else 0.0

        high_24h = round(max(current_price, open_price) + (base * vol * 0.7), 2)
        low_24h = round(min(current_price, open_price) - (base * vol * 0.7), 2)
        volume = int(params["avg_volume"] * (0.8 + (math.cos(minute_hash * 4) * 0.2)))

        return MarketQuote(
            symbol=sym,
            price=current_price,
            change=change,
            change_pct=change_pct,
            open=open_price,
            high_24h=high_24h,
            low_24h=low_24h,
            volume=volume,
            timestamp=now,
            is_demo=True,
        )

    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100,
    ) -> List[OHLCVBar]:
        sym = symbol.upper().strip()
        params = self._get_asset_params(sym)
        base_price = params["base_price"]
        daily_vol = params["daily_volatility"]
        avg_vol = params["avg_volume"]

        bars: List[OHLCVBar] = []
        now = datetime.now(timezone.utc).replace(hour=20, minute=0, second=0, microsecond=0)

        # Generate geometric walk backward then reverse
        # Use deterministic RNG seeded per symbol to keep chart consistent
        sym_seed = sum(ord(c) for c in sym) + self.seed
        rng = random.Random(sym_seed)

        # Step calculation based on timeframe
        if timeframe == "1h":
            delta = timedelta(hours=1)
        elif timeframe == "4h":
            delta = timedelta(hours=4)
        elif timeframe == "1w":
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(days=1)

        # Generate sequence
        price_series: List[float] = [base_price]
        cur = base_price
        for _ in range(limit):
            shock = rng.gauss(0.0003, daily_vol)
            cur = cur * (1.0 + shock)
            price_series.append(cur)

        # Rescale series so last price matches current base price
        scale = base_price / price_series[-1]
        adjusted_prices = [p * scale for p in price_series]

        for i in range(limit):
            bar_time = now - delta * (limit - 1 - i)
            # Skip weekends for daily equity bars
            if timeframe in ("1d", "1w") and bar_time.weekday() >= 5:
                bar_time -= timedelta(days=2)

            open_p = adjusted_prices[i]
            close_p = adjusted_prices[i + 1]
            high_extra = abs(rng.gauss(0, daily_vol * 0.6)) * max(open_p, close_p)
            low_extra = abs(rng.gauss(0, daily_vol * 0.6)) * min(open_p, close_p)

            high_p = round(max(open_p, close_p) + high_extra, 2)
            low_p = round(max(0.1, min(open_p, close_p) - low_extra), 2)
            open_p = round(open_p, 2)
            close_p = round(close_p, 2)

            vol_mult = 1.0 + (abs(close_p - open_p) / (open_p * daily_vol)) * 0.5
            bar_volume = int(avg_vol * vol_mult * rng.uniform(0.7, 1.3))

            bars.append(
                OHLCVBar(
                    timestamp=bar_time,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=bar_volume,
                )
            )

        return bars

    async def get_supported_symbols(self) -> List[SymbolInfo]:
        symbols_info: List[SymbolInfo] = []
        for sym, data in SUPPORTED_ASSETS.items():
            quote = await self.get_latest_quote(sym)
            symbols_info.append(
                SymbolInfo(
                    symbol=sym,
                    name=data["name"],
                    exchange=data["exchange"],
                    asset_class=data["asset_class"],
                    current_price=quote.price,
                    daily_change_pct=quote.change_pct,
                    is_demo=True,
                )
            )
        return symbols_info

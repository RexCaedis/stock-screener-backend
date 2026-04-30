import os
from typing import Dict, List

import requests

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
DEFAULT_STOCKS = [
    "AAPL", "AMD", "NVDA", "TSLA", "PLTR", "RIOT", "MARA", "FCEL", "CLSK", "SOFI",
    "HOOD", "RIVN", "LCID", "OPEN", "F", "NIO", "BBAI", "SOUN", "IONQ", "MARA"
]


def get_watchlist() -> List[str]:
    """Return symbols from STOCK_SYMBOLS env var, or a starter watchlist."""
    symbols = os.getenv("STOCK_SYMBOLS", "")
    if not symbols.strip():
        return DEFAULT_STOCKS
    return [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]


def get_stock_data(symbol: str, interval: str = "1min") -> Dict:
    if not API_KEY:
        return {"error": "Missing ALPHA_VANTAGE_API_KEY environment variable."}

    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": API_KEY,
            "outputsize": "compact",
        },
        timeout=20,
    )
    return response.json()


def _series_key(interval: str) -> str:
    return f"Time Series ({interval})"


def get_candles(symbol: str, interval: str = "1min") -> List[Dict]:
    data = get_stock_data(symbol.upper(), interval)
    key = _series_key(interval)
    series = data.get(key, {})

    candles = []
    for timestamp, row in sorted(series.items()):
        candles.append({
            "time": timestamp,
            "open": float(row["1. open"]),
            "high": float(row["2. high"]),
            "low": float(row["3. low"]),
            "close": float(row["4. close"]),
            "volume": int(float(row["5. volume"])),
        })
    return candles


def _safe_percent_change(open_price: float, close_price: float) -> float:
    if open_price == 0:
        return 0
    return ((close_price - open_price) / open_price) * 100


def get_filtered_stocks(
    min_price: float = 2,
    max_price: float = 20,
    min_volume: int = 500000,
    min_change: float = 5,
    min_relative_volume: float = 1,
    interval: str = "1min",
) -> List[Dict]:
    filtered = []

    for symbol in get_watchlist():
        candles = get_candles(symbol, interval)
        if not candles:
            continue

        latest = candles[-1]
        close_price = latest["close"]
        open_price = latest["open"]
        percent_change = _safe_percent_change(open_price, close_price)
        volume = latest["volume"]

        previous_candles = candles[-21:-1]
        average_volume = sum(candle["volume"] for candle in previous_candles) / len(previous_candles) if previous_candles else volume
        relative_volume = volume / average_volume if average_volume else 0

        matches = (
            min_price <= close_price <= max_price
            and volume >= min_volume
            and percent_change >= min_change
            and relative_volume >= min_relative_volume
        )

        if matches:
            filtered.append({
                "symbol": symbol,
                "price": round(close_price, 2),
                "change": round(percent_change, 2),
                "volume": volume,
                "relativeVolume": round(relative_volume, 2),
                "matchedCriteria": [
                    f"Price ${min_price:g}-${max_price:g}",
                    f"Volume ≥ {min_volume:,}",
                    f"Change ≥ {min_change:g}%",
                    f"RelVol ≥ {min_relative_volume:g}x",
                ],
                "lastMatched": latest["time"],
            })

    return filtered

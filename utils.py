import os
import time
from typing import Dict, List

import requests

API_KEY = os.getenv("FINNHUB_API_KEY", "")
DEFAULT_STOCKS = [
    "AAPL", "AMD", "NVDA", "TSLA", "PLTR", "RIOT", "MARA", "FCEL", "CLSK", "SOFI",
    "HOOD", "RIVN", "LCID", "OPEN", "F", "NIO", "BBAI", "SOUN", "IONQ"
]


def get_watchlist() -> List[str]:
    """Return symbols from STOCK_SYMBOLS env var, or a starter watchlist."""
    symbols = os.getenv("STOCK_SYMBOLS", "")
    if not symbols.strip():
        return DEFAULT_STOCKS
    return [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]


def _resolution(interval: str) -> str:
    mapping = {
        "1min": "1",
        "5min": "5",
        "15min": "15",
        "30min": "30",
        "60min": "60",
        "1h": "60",
        "1d": "D",
    }
    return mapping.get(interval, "1")


def get_stock_quote(symbol: str) -> Dict:
    if not API_KEY:
        return {"error": "Missing FINNHUB_API_KEY environment variable."}

    response = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={"symbol": symbol.upper(), "token": API_KEY},
        timeout=20,
    )
    return response.json()


def get_stock_data(symbol: str, interval: str = "1min") -> Dict:
    """Compatibility helper used by /debug. Returns Finnhub quote data."""
    return get_stock_quote(symbol)


def get_candles(symbol: str, interval: str = "1min") -> List[Dict]:
    if not API_KEY:
        return []

    now = int(time.time())
    start = now - 60 * 60 * 24 * 5

    response = requests.get(
        "https://finnhub.io/api/v1/stock/candle",
        params={
            "symbol": symbol.upper(),
            "resolution": _resolution(interval),
            "from": start,
            "to": now,
            "token": API_KEY,
        },
        timeout=20,
    )
    data = response.json()

    if data.get("s") != "ok":
        return []

    candles = []
    for index, timestamp in enumerate(data.get("t", [])):
        candles.append({
            "time": timestamp,
            "open": float(data["o"][index]),
            "high": float(data["h"][index]),
            "low": float(data["l"][index]),
            "close": float(data["c"][index]),
            "volume": int(float(data["v"][index])),
        })
    return candles


def _safe_percent_change(previous_close: float, current_price: float) -> float:
    if previous_close == 0:
        return 0
    return ((current_price - previous_close) / previous_close) * 100


def get_filtered_stocks(
    min_price: float = 2,
    max_price: float = 20,
    min_volume: int = 500000,
    min_change: float = 5,
    min_relative_volume: float = 0,
    interval: str = "1min",
) -> List[Dict]:
    filtered = []

    for symbol in get_watchlist():
        quote = get_stock_quote(symbol)
        if quote.get("error"):
            continue

        current_price = float(quote.get("c") or 0)
        previous_close = float(quote.get("pc") or 0)
        percent_change = _safe_percent_change(previous_close, current_price)

        candles = get_candles(symbol, interval)
        latest_volume = candles[-1]["volume"] if candles else 0
        previous_candles = candles[-21:-1]
        average_volume = sum(candle["volume"] for candle in previous_candles) / len(previous_candles) if previous_candles else latest_volume
        relative_volume = latest_volume / average_volume if average_volume else 0
        last_matched = candles[-1]["time"] if candles else None

        matches = (
            min_price <= current_price <= max_price
            and latest_volume >= min_volume
            and percent_change >= min_change
            and relative_volume >= min_relative_volume
        )

        if matches:
            filtered.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(percent_change, 2),
                "volume": latest_volume,
                "relativeVolume": round(relative_volume, 2),
                "matchedCriteria": [
                    f"Price ${min_price:g}-${max_price:g}",
                    f"Volume ≥ {min_volume:,}",
                    f"Change ≥ {min_change:g}%",
                    f"RelVol ≥ {min_relative_volume:g}x",
                ],
                "lastMatched": last_matched,
            })

    return filtered

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from utils import get_filtered_stocks, get_candles, get_stock_data, get_watchlist

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Stock screener backend is running."}


@app.get("/health")
def health():
    return {"status": "ok", "watchlist": get_watchlist()}


@app.get("/debug/{symbol}")
def debug_symbol(symbol: str, interval: str = Query("1min")):
    data = get_stock_data(symbol, interval)
    series_key = f"Time Series ({interval})"
    if series_key in data:
        latest_time = next(iter(data[series_key].keys()))
        latest = data[series_key][latest_time]
        return {
            "status": "ok",
            "symbol": symbol.upper(),
            "seriesKey": series_key,
            "latestTime": latest_time,
            "latestCandle": latest,
            "message": "Alpha Vantage returned candle data. The API key is working.",
        }
    return {
        "status": "error",
        "symbol": symbol.upper(),
        "seriesKeyExpected": series_key,
        "rawResponse": data,
        "message": "No candle data returned. Check the rawResponse for API key, rate limit, or symbol issues.",
    }


@app.get("/stocks")
def read_stocks(
    min_price: float = Query(2),
    max_price: float = Query(20),
    min_volume: int = Query(500000),
    min_change: float = Query(5),
    min_relative_volume: float = Query(0),
):
    return get_filtered_stocks(
        min_price=min_price,
        max_price=max_price,
        min_volume=min_volume,
        min_change=min_change,
        min_relative_volume=min_relative_volume,
    )


@app.get("/candles/{symbol}")
def read_candles(symbol: str, interval: str = Query("1min")):
    return get_candles(symbol, interval)

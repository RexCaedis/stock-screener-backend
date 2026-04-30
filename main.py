from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from utils import get_filtered_stocks, get_candles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/stocks")
def read_stocks(
    min_price: float = Query(2),
    max_price: float = Query(20),
    min_volume: int = Query(500000),
    min_change: float = Query(5),
    min_relative_volume: float = Query(1),
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

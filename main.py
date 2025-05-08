from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated stock data
@app.get("/stocks")
def get_stocks():
    return [
        {
            "symbol": "AAPL",
            "price": 173.51,
            "volume": 2100000,
            "change_percent": 4.2,
            "news": "Apple spikes on strong earnings",
            "chart_url": "https://example.com/aapl.png"
        },
        {
            "symbol": "TSLA",
            "price": 230.12,
            "volume": 3500000,
            "change_percent": 3.7,
            "news": "Tesla jumps after delivery beat",
            "chart_url": "https://example.com/tsla.png"
        }
    ]

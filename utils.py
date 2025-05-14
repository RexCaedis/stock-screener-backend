import requests

API_KEY = "YOUR_API_KEY"  # Replace with your Alpha Vantage or Finnhub API key
STOCKS = ["AAPL", "AMD", "NVDA", "TSLA", "PLTR", "RIOT", "MARA", "FCEL", "CLSK", "BBBY"]

def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def get_filtered_stocks():
    filtered = []
    for symbol in STOCKS:
        data = get_stock_data(symbol)
        try:
            times = list(data["Time Series (1min)"].keys())
            latest = data["Time Series (1min)"][times[0]]
            open_price = float(latest["1. open"])
            close_price = float(latest["4. close"])
            percent_change = ((close_price - open_price) / open_price) * 100
            volume = int(latest["5. volume"])

            if 3 <= close_price <= 20 and percent_change >= 20 and volume > 500000:
                filtered.append({
                    "symbol": symbol,
                    "price": close_price,
                    "change": round(percent_change, 2),
                    "volume": volume
                })
        except Exception:
            continue
    return filtered

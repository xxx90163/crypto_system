# fetch_kline.py

import requests
import pandas as pd


def fetch_kline(symbol="BTCUSDT", interval="5m", limit=200):

    url = "https://fapi.binance.com/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(url, params=params)
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "taker_base", "taker_quote", "ignore"
    ])

    df["close"] = df["close"].astype(float)

    return df

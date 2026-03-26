import requests
from config import BASE_URL, API_KEY

ENDPOINT = "/api/futures/liquidation/history"

def fetch_liquidation_data():
    headers = {
        "accept": "application/json",
        "CG-API-KEY": API_KEY
    }

    params = {
        "exchange": "Binance",
        "symbol": "BTCUSDT",
        "interval": "1h"
    }

    r = requests.get(BASE_URL + ENDPOINT, headers=headers, params=params, timeout=20)

    print("清算API狀態碼:", r.status_code)

    if r.status_code != 200:
        print("錯誤:", r.text)
        return {}

    return r.json()

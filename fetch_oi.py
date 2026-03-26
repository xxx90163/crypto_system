import requests

def fetch_oi():
    try:
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {
            "symbol": "BTCUSDT"
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        oi = float(data["openInterest"])

        print("✅ 當前 OI:", oi)

        return oi

    except Exception as e:
        print("❌ OI 取得失敗:", e)
        return 0

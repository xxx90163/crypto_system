import json

with open("steelx_live.json", "r") as f:
    data = json.load(f)

small_data = {}

for symbol in data:
    small_data[symbol] = {
        "klines": data[symbol]["klines"][-20:]
    }

print(json.dumps(small_data))

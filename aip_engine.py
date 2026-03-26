import json

from fetch_price import fetch_price
from fetch_oi import fetch_oi
from fetch_liquidation import fetch_liquidation_data
from parse_liquidation import parse_liquidation

from decision_engine import decide_direction
from trap_engine import detect_trap
from fake_break_engine import detect_fake_break
from entry_engine import decide_entry
from trade_mode_engine import decide_trade_mode
from risk_engine import calculate_risk

from execution_engine import simulate_execution
from verdict_engine import evaluate_trade


def build_aip():

    data = {}

    # 🔹 基礎資料
    data["price"] = fetch_price()
    data["oi"] = fetch_oi()

    raw_liq = fetch_liquidation_data()
    liq_data = parse_liquidation(raw_liq)
    data.update(liq_data)

    data["symbol"] = "BTCUSDT"
    data["funding_rate"] = 0.01
    data["long_ratio"] = 0.6
    data["short_ratio"] = 0.4

    # 🔹 判斷鏈
    data.update(decide_direction(data))
    data.update(detect_trap(data))
    data.update(detect_fake_break(data))
    data.update(decide_entry(data))
    data.update(decide_trade_mode(data))
    data.update(calculate_risk(data))

    # 🔥 V7：模擬執行
    exec_data = simulate_execution(data)
    data.update(exec_data)

    # 🔥 Verdict
    verdict_data = evaluate_trade(data)
    data.update(verdict_data)

    return data


def save_json(data):
    with open("output.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    data = build_aip()
    save_json(data)

    print("💀 Steel X AIP v7（模擬下單 + 審判）")
    print(data)

# execution_engine.py

def simulate_execution(data):

    entry = data.get("entry")
    stop = data.get("stop_loss")
    direction = data.get("direction", "")
    can_trade = data.get("can_trade", False)

    if not can_trade or entry is None:
        return {
            "execution": "SKIP",
            "pnl": 0,
            "result": "NO_TRADE"
        }

    # 🔥 模擬市場（簡化版）
    price_now = data.get("price", entry)

    # 模擬波動（假設上下1%）
    up_move = price_now * 1.01
    down_move = price_now * 0.99

    pnl = 0
    result = "UNKNOWN"

    if "下" in direction:
        # 空單
        if down_move < entry:
            pnl = entry - down_move
            result = "WIN"
        elif up_move > stop:
            pnl = stop - entry
            result = "LOSS"

    elif "上" in direction:
        # 多單
        if up_move > entry:
            pnl = up_move - entry
            result = "WIN"
        elif down_move < stop:
            pnl = stop - entry
            result = "LOSS"

    return {
        "execution": "SIMULATED",
        "pnl": round(pnl, 2),
        "result": result
    }

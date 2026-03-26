# verdict_engine.py

def evaluate_trade(data):

    result = data.get("result", "UNKNOWN")
    pnl = data.get("pnl", 0)

    if result == "WIN":
        verdict = "✅ 好交易"
    elif result == "LOSS":
        verdict = "❌ 壞交易"
    else:
        verdict = "⚠ 無效交易"

    return {
        "verdict": verdict,
        "pnl_score": pnl
    }

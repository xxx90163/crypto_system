def decide_trade_mode(data):
    strength = data.get("strength_ratio", 1)

    # 🔥 模式判斷
    if strength > 1.2:
        mode = "TREND"
    elif strength < 0.8:
        mode = "REVERSAL"
    else:
        mode = "RANGE"

    # 🔥 關鍵：允許交易
    can_trade = True
    reason = "允許交易"

    # ⚠️ 只有極端才禁止
    if 0.98 < strength < 1.02:
        can_trade = False
        reason = "完全無方向"

    return {
        "mode": mode,
        "confidence": round(strength, 2),
        "can_trade": can_trade,
        "trade_reason": reason
    }

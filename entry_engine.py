# entry_engine.py

def decide_entry(data):

    direction = data.get("direction", "中性")
    liq_above = data.get("liq_above", 0)
    liq_below = data.get("liq_below", 0)
    price = data.get("price", 0)

    action = "觀望"
    zone = "無"
    mode = "NO_TRADE"
    confidence = 0.5

    # 🔥 如果上方清算比較多 → 等上掃再空
    if liq_above > liq_below:
        action = "⌛ 等上掃再空"
        zone = f"{int(price*1.01)} - {int(price*1.03)}"
        mode = "SWEEP_SHORT"
        confidence = 0.7

    # 🔥 如果下方清算比較多 → 等下掃再多
    elif liq_below > liq_above:
        action = "⌛ 等下掃再多"
        zone = f"{int(price*0.97)} - {int(price*0.99)}"
        mode = "SWEEP_LONG"
        confidence = 0.7

    # 🔥 沒明顯方向
    else:
        action = "🚫 不交易"
        zone = "-"
        mode = "NO_TRADE"
        confidence = 0.3

    return {
        "entry_action": action,
        "entry_zone": zone,
        "mode": mode,
        "confidence": round(confidence, 2)
    }

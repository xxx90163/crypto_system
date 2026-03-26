# decision_engine.py

def decide_direction(data):

    liq_above = data.get("liq_above", 0)
    liq_below = data.get("liq_below", 0)

    # 判斷掃單方向
    if liq_above > liq_below:
        direction = "⬆ 往上掃"
    elif liq_below > liq_above:
        direction = "⬇ 往下掃"
    else:
        direction = "⚖ 中性"

    # 強度比
    ratio = 0
    if liq_below != 0:
        ratio = liq_above / liq_below

    return {
        "direction": direction,
        "strength_ratio": round(ratio, 2)
    }

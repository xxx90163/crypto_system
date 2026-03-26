# fake_break_engine.py

def detect_fake_break(data):

    liq_above = data.get("liq_above", 0)
    liq_below = data.get("liq_below", 0)

    fake_prob = 0
    signal = "正常"

    # 🔥 上方假突破
    if liq_above > liq_below * 1.5:
        fake_prob = 0.7
        signal = "⚠ 上方假突破風險"

    # 🔥 下方假跌破
    elif liq_below > liq_above * 1.5:
        fake_prob = 0.7
        signal = "⚠ 下方假跌破風險"

    else:
        fake_prob = 0.3
        signal = "正常"

    return {
        "fake_break_risk": signal,
        "fake_break_prob": fake_prob
    }

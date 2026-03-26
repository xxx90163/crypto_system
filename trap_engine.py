# trap_engine.py

def detect_trap(data):

    long_ratio = data.get("long_ratio", 0.5)
    short_ratio = data.get("short_ratio", 0.5)
    funding = data.get("funding_rate", 0)

    trap = "無"

    # 🔥 多單過多 → 往下殺
    if long_ratio > 0.7:
        trap = "⚠ 多單陷阱（偏空）"

    # 🔥 空單過多 → 往上掃
    elif short_ratio > 0.7:
        trap = "⚠ 空單陷阱（偏多）"

    # 🔥 funding 過熱
    if funding > 0.03:
        trap = "⚠ 過熱做多（可能反殺）"

    elif funding < -0.03:
        trap = "⚠ 過度做空（可能反彈）"

    return {
        "trap_warning": trap
    }

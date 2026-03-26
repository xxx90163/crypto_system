# risk_engine.py

def calculate_risk(data):
    price = data.get("price", 0)
    direction = data.get("direction", "中性")
    mode = data.get("mode", "RANGE")
    can_trade = data.get("can_trade", False)

    # 預設
    entry = None
    stop_loss = None
    position_size = 0
    rr_ratio = 0

    if not can_trade:
        return {
            "entry": None,
            "stop_loss": None,
            "position_size": 0,
            "rr_ratio": 0,
            "risk_status": "❌ 不可交易"
        }

    # 🔥 根據方向設定
    if "下" in direction:
        entry = price * 1.002   # 等反彈再空
        stop_loss = price * 1.01
    elif "上" in direction:
        entry = price * 0.998   # 等回踩再多
        stop_loss = price * 0.99

    # 🔥 倉位（簡化版）
    position_size = 0.1  # 10%

    # 🔥 RR（簡單估）
    if entry and stop_loss:
        risk = abs(entry - stop_loss)
        reward = risk * 2
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0

    return {
        "entry": round(entry, 2) if entry else None,
        "stop_loss": round(stop_loss, 2) if stop_loss else None,
        "position_size": position_size,
        "rr_ratio": rr_ratio,
        "risk_status": "✅ 可交易"
    }

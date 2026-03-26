def parse_liquidation(raw_data):

    data = raw_data.get("data", [])

    total_long = 0.0
    total_short = 0.0

    for item in data:
        try:
            long_val = float(item.get("long_liquidation_usd", 0))
            short_val = float(item.get("short_liquidation_usd", 0))
        except:
            long_val = 0
            short_val = 0

        total_long += long_val
        total_short += short_val

    return {
        "liq_above": total_short,
        "liq_below": total_long
    }

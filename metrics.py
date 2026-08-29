def to_float(s):
    if s is None:
        return None

    try:
        return float(str(s).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def calc_metrics(data: dict) -> dict:
    def get_value(field_name):
        if not isinstance(data, dict):
            return None

        if field_name in data and isinstance(data[field_name], dict):
            return data[field_name].get("value")

        for group_name in ["main", "income", "balance"]:
            group_data = data.get(group_name)
            if isinstance(group_data, dict) and field_name in group_data:
                field_data = group_data.get(field_name)
                if isinstance(field_data, dict):
                    return field_data.get("value")

        return None

    revenue_raw = get_value("营业收入")
    cost_raw = get_value("营业成本")
    liabilities_raw = get_value("负债合计")
    assets_raw = get_value("资产总计")

    revenue = to_float(revenue_raw)
    cost = to_float(cost_raw)
    liabilities = to_float(liabilities_raw)
    assets = to_float(assets_raw)

    if revenue is None or cost is None or revenue == 0:
        gross_margin = {"value": None, "formula": None}
    else:
        gross_margin = {
            "value": f"{((revenue - cost) / revenue) * 100:.2f}%",
            "formula": f"({revenue_raw} - {cost_raw}) / {revenue_raw}",
        }

    if liabilities is None or assets is None or assets == 0:
        debt_ratio = {"value": None, "formula": None}
    else:
        debt_ratio = {
            "value": f"{(liabilities / assets) * 100:.2f}%",
            "formula": f"{liabilities_raw} / {assets_raw}",
        }

    return {
        "毛利率": gross_margin,
        "资产负债率": debt_ratio,
    }

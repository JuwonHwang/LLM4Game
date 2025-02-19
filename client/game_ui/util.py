def unit_to_shop_text(unit: dict):
    if unit is None:
        return "\n"
    name = unit['name']
    level = unit['level']
    star = '⭐'* level
    cost = unit['cost']
    return f"🪙{cost}\n{star} {name}"

def unit_to_text(unit: dict):
    if unit is None:
        return ""
    name = unit['name']
    level = unit['level']
    star = '⭐'* level
    return f"{star} {name}"
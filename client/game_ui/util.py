import unicodedata

def unit_to_shop_text(unit: dict):
    if unit is None:
        return "\n"
    name = unit['name']
    level = unit['level']
    star = '⭐'* level
    cost = unit['cost']
    emo = unicodedata.lookup(name)
    return f"{cost}🪙 {star}\n{emo} {name}"

def unit_to_text(unit: dict):
    if unit is None:
        return "\n"
    name = unit['name']
    level = unit['level']
    star = '⭐'* level
    try:
        emo = unicodedata.lookup(name)
    except:
        emo = ''
    return f"{star}\n{emo} {name}"
import unicodedata
from pyautobattle.src.util import get_info, get_name, get_cost, get_price

color_map = [
    "#A4A4A4",  
    "#413a41",  
    "#173f29",  
    "#3498db",  
    "#9b59b6",  
    "#f1c40f"   
]
hover_color_map = [
    "#A4A4A4",  
    "#615a61",  
    "#375f49",  
    "#5dade2",  
    "#af7ac5",  
    "#f4d03f"   
]

def get_color(unit):
    if unit is not None:
        cost = get_cost(unit)
        return color_map[cost], hover_color_map[cost]
    else:
        return "#eeeeee", "#eeeeee"

def unit_to_shop_text(unit: dict):
    if unit is None:
        return "\n"
    name = get_name(unit)
    level = unit['level']
    star = '⭐'* level
    cost = get_cost(unit)
    try:
        emo = unicodedata.lookup(name)
    except:
        emo = ''
    return f"{cost}🪙 {star}\n{emo} {name}"

def unit_to_text(unit: dict):
    if unit is None:
        return "\n"
    name = get_name(unit)
    level = unit['level']
    star = '⭐'* level
    try:
        emo = unicodedata.lookup(name)
    except:
        emo = ''
    return f"{star}\n{emo} {name}"
import unicodedata

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

import csv

unit_info = {}
with open("./memory/unit.csv", mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        unit_info[row["unit_id"]] = row

def get_info(unit):
    if unit is not None:
        return unit_info[unit["id"]]
    return {
        'unit_id': "unit_0",
        'name': "Unknown",
        'cost': 0,
        'level': 1,
        'synergy': [],
        'item': [],
        "hp": 0, "mp": 0, "attack": 0, "defense": 0, "attackSpeed": 0,
        "specialAttack": 0, "specialDefense": 0, "criticalRate": 0,
        "criticalDamage": 1, "attackRange": 0,
    }

def get_name(unit):
    try:
        return unit_info[unit["id"]]["name"]
    except:
        return "Unknown"
        
def get_cost(unit):
    try:
        return int(unit_info[unit["id"]]["cost"])
    except:
        return 0

def get_price(unit):
    cost = get_cost(unit)
    level = int(unit["level"])
    if cost == 1:
        return int(cost * (3 ** (level - 1)))
    else:
        return int(cost * (3 ** (level - 1)) - 1 if level > 1 else cost)

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
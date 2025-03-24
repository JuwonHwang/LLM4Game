import csv
from enum import Enum

class TEAM(Enum):
    HOME = "home"
    AWAY = "away"

unit_info = {}
with open("./pyautobattle/data/unit.csv", mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        unit_info[row["unit_id"]] = row
        
def get_unit_dict():
    unit_dict = {}
    for k, v in unit_info.items():
        unit_dict[k] = {
            "cost": v["cost"],
            "hp": v["hp"],
            "attack": v["attack"],
            "defense": v["defense"],
            "attackRange": v["attackRange"]
        }
    return unit_dict

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
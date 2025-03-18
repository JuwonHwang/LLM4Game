import csv

unit_info = {}
with open("./memory/unit.csv", mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        unit_info[row["unit_id"]] = row
        
def get_cost(unit):
    return int(unit_info[unit['id']]["cost"])

def get_price(unit):
    cost = get_cost(unit)
    level = int(unit["level"])
    if cost == 1:
        return int(cost * (3 ** (level - 1)))
    else:
        return int(cost * (3 ** (level - 1)) - 1 if level > 1 else cost)
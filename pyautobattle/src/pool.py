import csv
import json
from .status import Status
from .unit import Unit
import copy

class Pool:
    def __init__(self, unit_file):
        self.unit_counts = [0, 22, 20, 17, 10, 9]
        self.unit_dict:dict[str, Unit] = dict()
        self.available_units = [
            {},
            {},
            {},
            {},
            {},
            {}
        ]
        self.register_unit(unit_file)

    def register_unit(self, unit_csv_file_name: str):
        # Define the path to your CSV file
        file_path = unit_csv_file_name
        # Open and read the CSV file
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                name = row["name"]
                cost = int(row["cost"])
                unit_status = Status(
                    float(row["hp"]),
                    float(row["mp"]),
                    float(row["attack"]),
                    float(row["defense"]),
                    float(row["attackSpeed"]),
                    float(row["specialAttack"]),
                    float(row["specialDefense"]),
                    float(row["criticalRate"]),
                    float(row["criticalDamage"]),
                    int(row["attackRange"]),
                )
                _unit = Unit(name, cost, 1, unit_status, [])
                self.unit_dict[name] = _unit
                count = self.unit_counts[cost]
                self.available_units[cost][name] = count

    
    def get_unit(self, unit_name: str, unit_level: int):
        _unit = copy.deepcopy(self.unit_dict[unit_name])
        _unit.level = unit_level
        coefficient = 1.6 ** unit_level
        _unit.status = Status(
            hp=_unit.status.hp * coefficient,
            mp=_unit.status.mp,
            attack= _unit.status.attack * coefficient,
            defense= _unit.status.defense * coefficient,
            attackSpeed= _unit.status.attackSpeed,
            specialAttack= _unit.status.specialAttack,
            specialDefense= _unit.status.specialDefense * coefficient,
            criticalRate= _unit.status.criticalRate,
            criticalDamage= _unit.status.criticalDamage,
            attackRange= _unit.status.attackRange
        )
        return _unit
    
    def remove_unit(self, _unit: Unit):
        name = _unit.name
        level = _unit.level
        cost = _unit.cost
        unit_num = int(3 ** (level - 1))
        self.available_units[cost][name] -= unit_num

    def add_unit(self, _unit: Unit):
        name = _unit.name
        level = _unit.level
        cost = _unit.cost
        unit_num = int(3 ** (level - 1))
        self.available_units[cost][name] += unit_num
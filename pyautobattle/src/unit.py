from .active import Active
from .status import Status
import json
import math
import random
import copy
# from .color import *

class Unit(Active):
    def __init__(self, name: str, cost: int, level: int, status: Status, synergy: list[str]):
        super().__init__()
        self.synergy = synergy
        self.cost = cost
        self.name = name
        self.level = level
        self.status = status
        self.additional_status = Status(0,0,0,0,0,0,0,0,0,0)
        self.items = []
        self.cooldown_time = 0
        self.mana = 0
        self.live = True
        
    def observe(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "level": self.level,
            "synergy": self.synergy,
            "item": [item.observe() for item in self.items],
            "status": self.status.observe()
        }

    def to_json(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "price": self.get_sell_gold(),
            "level": self.level,
            "synergy": self.synergy,
            "item": [item.to_json() for item in self.items],
            "mana": self.mana,
            "status": self.status.to_json()
        }

    def get_combat_mode(self):
        return json.loads(json.dumps(self.observe()))

    def get_sell_gold(self):
        if self.cost == 1:
            return int(self.cost * (3 ** (self.level - 1)))
        else:
            return int(self.cost * (3 ** (self.level - 1)) - 1 if self.level > 1 else self.cost)

    def die(self):
        self.live = False

    def update(self):
        self.cooldown()

    def cooldown(self):
        self.cooldown_time -= 1 / 1000

    def hit(self, other):
        if not isinstance(other, Unit):
            raise NotImplementedError("not Unit:", other)
        is_critical = random.random() < (self.status.criticalRate / 100)
        damage_rate = self.status.criticalDamage if is_critical else 1.0
        defense_rate = 100 / (100 + other.status.defense)
        damage = self.status.attack * defense_rate * damage_rate
        other.status.hp -= damage
        self.mana += 20
        killed = False
        if other.status.hp <= 0:
            other.die()
            killed = True
        return {
            "attacker": (self.name, id(self)),
            "defender": (other.name, id(other)),
            "damage": round(damage),
            "critical": is_critical,
            "killed": killed
        }
    
    def __deepcopy__(self, memo):
        # Create a new Unit instance with deep-copied initial values
        unit_copy = Unit(
            copy.deepcopy(self.name, memo),
            copy.deepcopy(self.cost, memo),
            copy.deepcopy(self.level, memo),
            copy.deepcopy(self.status, memo),
            copy.deepcopy(self.synergy, memo)
        )
        # Deep copy additional attributes
        self.cooldown_time = copy.deepcopy(self.cooldown_time, memo)
        self.mana = copy.deepcopy(self.mana, memo)
        unit_copy.additional_status = copy.deepcopy(self.additional_status, memo)
        unit_copy.items = copy.deepcopy(self.items, memo)
        unit_copy.live = self.live  # boolean value, shallow copy is fine
        return unit_copy
from .active import Active
from .status import Status
import json

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
        
    def observe(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "level": self.level,
            "synergy": self.synergy,
            "item": [item.observe() for item in self.items],
            "status": self.status.observe()
        }
    
    def get_combat_mode(self):
        return json.loads(json.dumps(self.observe()))
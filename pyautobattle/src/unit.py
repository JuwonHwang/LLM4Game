from .active import Active
from .status import Status

class Unit(Active, Status):
    def __init__(self, name: str, cost: int, status: Status, synergy: list[str]):
        super().__init__()
        self.synergy = []
        self.cost = cost
        self.name = name
        
        
    def observe(self):
        pass
from .base import Base
from .unit import Unit
class Bench(Base):
    def __init__(self):
        self.max_units = 10
        self.units: list[Unit] = []
        
    def observe(self):
        return [u.observe() for u in self.units]
    
    def count(self, unit_name, unit_level):
        n = 0
        for unit in self.units:
            if unit.name == unit_name and unit.level == unit_level:
                n += 1
        return n
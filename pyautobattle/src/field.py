from .base import Base
from .unit import Unit


class Field(Base):
    def __init__(self):
        self.max_units = 1
        self.units: list[Unit] = []
        
    def observe(self):
        return [u.observe() for u in self.units]
    
    def get_combat_mode(self):
        return [u.get_combat_mode() for u in self.units]
    
    def count(self, unit_name, unit_level):
        n = 0
        for unit in self.units:
            if unit.name == unit_name and unit.level == unit_level:
                n += 1
        return n
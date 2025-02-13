from .base import Base
from .unit import Unit
import copy

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
    
    def update(self):
        for u in self.units:
            u.update()
    
    def __deepcopy__(self, memo):
        # Create a new instance of Field
        field_copy = type(self)()
        # Copy the max_units attribute
        field_copy.max_units = self.max_units
        # Deep copy the units list
        field_copy.units = copy.deepcopy(self.units, memo)
        # Store the new object in the memo dictionary
        memo[id(self)] = field_copy
        return field_copy
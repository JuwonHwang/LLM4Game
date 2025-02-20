from .base import EMPTY
from .unit import Unit
from .bench import Bench
import copy

class Field(Bench):
    def __init__(self):
        self.max_units = 1
        self.num_slots = 4 * 7
        self.units: list[Unit] = [None] * self.num_slots
        
    def is_full(self):
        nones = self.units.count(None)
        return self.num_slots - nones >= self.max_units
    
    def get_combat_mode(self):
        return [u.get_combat_mode() for u in self.units]
    
    def level_up(self):
        self.max_units += 1
        # self.units.append(None)
    
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
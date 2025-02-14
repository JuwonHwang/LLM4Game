from .base import Base, EMPTY
from .unit import Unit
import copy

class Field(Base):
    def __init__(self):
        self.max_units = 1
        self.units: list[Unit] = []
        
    def observe(self):
        return [u.observe() for u in self.units]
    
    def is_full(self):
        return len(self.units) >= self.max_units
    
    def __str__(self):
        field_text = "Field |"
        col = 0
        row = 0
        cells = [[]]
        for u in self.units:
            if len(cells[row]) == 5:
                row += 1
                cells.append([])
            cells[row].append(u)
        num_empty = self.max_units - len(self.units)
        for i in range(num_empty):
            if len(cells[row]) == 5:
                row += 1
                cells.append([])
            cells[row].append(EMPTY)
        field_text += '|\n      |'.join(['| '.join([str(u) for u in row]) for row in cells])
        return field_text + '|'
    
    def get_combat_mode(self):
        return [u.get_combat_mode() for u in self.units]

    def count(self, unit_name, unit_level):
        n = 0
        for unit in self.units:
            if unit.name == unit_name and unit.level == unit_level:
                n += 1
        return n
    
    def remove(self, unit_name, unit_level):
        for unit in self.units:
            if unit.name == unit_name and unit.level == unit_level:
                self.units.remove(unit)
                return unit
    
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
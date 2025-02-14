from .base import Base, EMPTY
from .unit import Unit
import copy

class Bench(Base):
    def __init__(self):
        self.max_units = 10
        self.units: list[Unit] = []
        
    def observe(self):
        return [u.observe() for u in self.units]
    
    def is_full(self):
        return len(self.units) >= self.max_units
    
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
    
    def __str__(self):
        text = "Bench |"
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
        text += '|\n      |'.join(['| '.join([str(u) for u in row]) for row in cells])
        return text + '|'
from .base import Base, EMPTY
from .unit import Unit
import copy

class Bench(Base):
    def __init__(self):
        self.max_units = 10
        self.units: list[Unit] = []
        
    def pop(self, index):
        return self.units.pop(index)

    def insert(self, index, object):
        if index < self.max_units:
            self.units.insert(index, object)
        else:
            raise ValueError()
    
    def __len__(self):
        return len(self.units)
            
    def observe(self):
        return self.__str__()
    
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
        text += '|\n      |'.join(['|'.join([str(u) for u in row]) for row in cells])
        return text + '|'
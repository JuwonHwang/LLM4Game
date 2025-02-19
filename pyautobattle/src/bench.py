from .base import Base, EMPTY
from .unit import Unit
import copy

class Bench(Base):
    def __init__(self):
        self.max_units = 9
        self.units: list[Unit] = [None] * self.max_units
        
    def find_empty(self):
        for i, unit in enumerate(self.units):
            if unit is None:
                return i
        return -1
    
    def add(self, unit: Unit):
        index = self.find_empty()
        if index == -1:
            return -1
        else:
            self.units[index] = unit
            return index
        
    def pop(self, index):
        unit = self.units[index]
        self.units[index] = None
        return unit

    def insert(self, index, object):
        if index < self.max_units:
            self.units.insert(index, object)
        else:
            raise ValueError()
    
    def to_json(self):
        return {
            'max_units': self.max_units,
            'units': [unit.to_json() if unit is not None else None for unit in self.units]
        }
    
    def __len__(self):
        return len(self.units)
            
    def observe(self):
        return self.__str__()
    
    def is_full(self):
        return self.find_empty() == -1
    
    def count(self, unit_name, unit_level):
        n = 0
        for unit in self.units:
            if unit is not None:
                if unit.name == unit_name and unit.level == unit_level:
                    n += 1
        return n
    
    def remove(self, unit_name, unit_level):
        for i, unit in enumerate(self.units):
            if unit is not None:
                if unit.name == unit_name and unit.level == unit_level:
                    self.units[i] = None
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
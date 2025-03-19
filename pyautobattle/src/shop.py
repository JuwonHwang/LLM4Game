from .base import Base, EMPTY
from .unit import Unit
from .bench import Bench

class Shop(Bench):
    def __init__(self):
        self.max_units = 5
        self.num_slots = 5
        self.units: list[Unit] = [None] * self.max_units
        
    def observe(self):
        return self.__str__()
    
    def clear(self):
        self.units = []
from .base import Base, EMPTY
from .unit import Unit
from .color import yellow

class Shop(Base):
    def __init__(self):
        self.max_units = 5
        self.units: list[Unit] = [None] * self.max_units
        
    def observe(self):
        return self.__str__()
    
    def clear(self):
        self.units = []

    def __str__(self):
        unit_text = "Shop  |" + '|'.join([str(u) if u is not None else EMPTY for u in self.units]) + '|'
        cost_text = "      |" + '|'.join([yellow(f"         ${u.cost}         ") if u is not None else EMPTY for u in self.units]) + '|'
        return '\n'.join([unit_text, cost_text])
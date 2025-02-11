from .base import Base
from .unit import Unit

class Shop(Base):
    def __init__(self):
        self.max_units = 5
        self.units: list[Unit] = [None] * self.max_units
        
    def observe(self):
        return self.units
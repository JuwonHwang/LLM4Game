from .base import Base

class Shop(Base):
    def __init__(self):
        self.max_units = 5
        self.units = []
        
    def observe(self):
        return self.units
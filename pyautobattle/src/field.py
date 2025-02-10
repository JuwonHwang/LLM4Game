from .base import Base

class Field(Base):
    def __init__(self):
        self.max_units = 1
        self.units = []
        
    def observe(self):
        return [u.observe() for u in self.units]
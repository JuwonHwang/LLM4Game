from .base import Base

class Bench(Base):
    def __init__(self):
        self.max_units = 10
        self.units = []
        
    def observe(self):
        return [u.observe() for u in self.units]
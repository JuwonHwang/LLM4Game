from .base import Base

class Status(Base):
    def __init__(self):
        self.hp = 0
        self.mp = 0
        self.attack = 0
        self.defense = 0
        self.attackSpeed = 0
        self.specialAttack = 0
        self.specialDefense = 0
        self.criticalRate = 0
        self.criticalDamage = 0
        self.range = 0
    
    def observe(self):
        pass
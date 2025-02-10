from .base import Base

class Status(Base):
    def __init__(
            self, 
            hp,
            mp, 
            attack, 
            defense,
            attackSpeed, 
            specialAttack, 
            specialDefense, 
            criticalRate, 
            criticalDamage, 
            attackRange
        ):
        self.hp = float(hp)
        self.mp = float(mp)
        self.attack = float(attack)
        self.defense = float(defense)
        self.attackSpeed = float(attackSpeed)
        self.specialAttack = float(specialAttack)
        self.specialDefense = float(specialDefense)
        self.criticalRate = float(criticalRate)
        self.criticalDamage = float(criticalDamage)
        self.attackRange = int(attackRange)
    
    def observe(self):
        return {
            "hp": self.hp,
            "mp": self.mp,
            "attack": self.attack,
            "defense": self.defense,
            "attackSpeed": self.attackSpeed,
            "specialAttack": self.specialAttack,
            "specialDefense": self.specialDefense,
            "criticalRate": self.criticalRate,
            "criticalDamage": self.criticalDamage,
            "attackRange": self.attackRange,
        }
    
    def __add__(self, other):
        if isinstance(other, Status):
            return Status(
                    self.hp + other.hp,
                    self.mp + other.mp,
                    self.attack + other.attack,
                    self.defense + other.defense,
                    self.attackSpeed + other.attackSpeed,
                    self.specialAttack + other.specialAttack,
                    self.specialDefense + other.specialDefense,
                    self.criticalRate + other.criticalRate,
                    self.criticalDamage + other.criticalDamage,
                    self.attackRange + other.attackRange
                )
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Status):
            return Status(
                    self.hp - other.hp,
                    self.mp - other.mp,
                    self.attack - other.attack,
                    self.defense - other.defense,
                    self.attackSpeed - other.attackSpeed,
                    self.specialAttack - other.specialAttack,
                    self.specialDefense - other.specialDefense,
                    self.criticalRate - other.criticalRate,
                    self.criticalDamage - other.criticalDamage,
                    self.attackRange - other.attackRange
                )
        return NotImplemented
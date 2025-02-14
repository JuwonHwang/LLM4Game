from .base import Base
import copy

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
        self.hp = float(hp, 2)
        self.mp = float(mp, 2)
        self.attack = float(attack, 2)
        self.defense = float(defense, 2)
        self.attackSpeed = float(attackSpeed, 2)
        self.specialAttack = float(specialAttack, 2)
        self.specialDefense = float(specialDefense, 2)
        self.criticalRate = float(criticalRate, 2)
        self.criticalDamage = float(criticalDamage, 2)
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
    
    def __deepcopy__(self, memo):
        # Create a new instance of Status with deep-copied attributes
        new_copy = type(self)(
            self.hp,
            self.mp,
            self.attack,
            self.defense,
            self.attackSpeed,
            self.specialAttack,
            self.specialDefense,
            self.criticalRate,
            self.criticalDamage,
            self.attackRange
        )
        # Store the new object in the memo dictionary
        memo[id(self)] = new_copy
        return new_copy
from .base import Base
from .bench import Bench
from .shop import Shop
from .field import Field

class Player(Base):
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.hp = 100
        self.field = Field()
        self.bench = Bench()
        self.shop = Shop()
        self.gold = 0
        self.level = 1
        self.exp = 0
        
    def observe(self):
        return {
            "id": self.player_id,
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "field": self.field.observe(),
            "bench": self.bench.observe(),
            "shop": self.shop.observe(),
            "gold": self.gold,
            "exp": self.exp
        }
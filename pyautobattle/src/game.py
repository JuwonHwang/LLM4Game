from .base import Base
from .unit import Unit
from .player import Player

class AutoBattlerGame(Base):
    def __init__(self, players, seed=0):
        self.seed = seed
        self.players: list[Player] = players
        self.round = 0
        self.units = []
        self.unit_dict : dict[str, Unit] = dict()
        self.unit_counts = [0, 22, 20, 17, 10, 9]
        self.available_units = [
            {},
            {},
            {},
            {},
            {},
            {}
        ]
        
    def observe(self):
        return {
            "seed": self.seed,
            "players": [p.observe() for p in self.players],
            "round": self.round,
            "available_units": self.available_units
        }
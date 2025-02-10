from .base import Base

class AutoBattlerGame(Base):
    def __init__(self, players, seed=0):
        self.seed = seed
        self.players = players
        self.round = 0
        self.available_units = [
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
        }
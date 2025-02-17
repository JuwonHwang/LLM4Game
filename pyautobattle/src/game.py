from .base import Base
from .player import Player
from src import *
from .pool import Pool

class AutoBattlerGame(Base):
    def __init__(self, unit_file, seed=0):
        self.seed = seed
        self.pool = Pool(unit_file)
        self.players = [Player(i, f"player_{i}", pool=self.pool) for i in range(8)]
        self.round = 0
        
    def observe(self):
        return {
            "seed": self.seed,
            "players": [p.observe() for p in self.players],
            "round": self.round,
        }
    
    def get_player_by_index(self, index):
        return self.players[index]

from .base import Base
from .player import Player
from .pool import Pool

class AutoBattlerGame(Base):
    def __init__(self, unit_file='pyautobattle/data/unit.csv', seed=0):
        self.seed = seed
        self.pool = Pool(unit_file)
        self.players = [Player(i, f"player_{i}", pool=self.pool) for i in range(8)]
        self.round = 0
    
    def start(self):
        for player in self.players:
            player.gold = 5
            player.bench.units.append(self.pool.sample(1))
        for player in self.players:
            player.refresh_shop()
        
    def step(self):
        for player in self.players:
            player.refresh_shop()
            player.get_turn_exp()
            player.get_turn_gold()
        self.round += 1
        
    def observe(self):
        return {
            "players": [p.observe() for p in self.players],
            "round": self.round,
        }
    
    def get_player_by_index(self, index):
        return self.players[index]
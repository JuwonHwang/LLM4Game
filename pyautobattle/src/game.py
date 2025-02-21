from .base import Base
from .player import Player
from .pool import Pool
import time
from enum import Enum

class GameState(Enum):
    READY = "ready"
    BATTLE = "battle"


class AutoBattlerGame(Base):
    def __init__(self, game_id, unit_file='pyautobattle/data/unit.csv', synergy_file='pyautobattle/data/synergy.json', seed=0):
        self.game_id = game_id
        self.seed = seed
        self.pool = Pool(unit_file, synergy_file)
        self.round = 0
        self.timer = 0
        self.state_time = 30
        self.winner = None
        self.players: list[Player] = []
        self.current_players = set()
        self.running = False
        self.state = GameState.READY

    def register(self, user_id):
        self.current_players.add(user_id)

    def quit(self, user_id):
        self.current_players.discard(user_id)
        return len(self.current_players)

    def start(self):
        for user_id in list(self.current_players):
            self.players.append(Player(user_id, f"{user_id}", pool=self.pool))
        while len(self.players) < 8:
            i = len(self.players)
            self.players.append(Player(f"{self.game_id}-{i}", f"{self.game_id}-{i}", pool=self.pool))
        for player in self.players:
            player.gold = 100
            player.bench.add(self.pool.sample(1))
        for player in self.players:
            player.refresh_shop()
        self.running = True
        self.setActive(True)

    def next_round(self):
        for player in self.players:
            player.refresh_shop()
            player.get_turn_exp()
            player.get_turn_gold()
        self.round += 1

    def setActive(self, value=True):
        for player in self.players:
            player.active = value

    def next_state(self):
        if self.state == GameState.READY: # READY -> BATTLE
            self.setActive(False)
            self.state = GameState.BATTLE

        elif self.state == GameState.BATTLE: # BATTLE -> READY
            self.setActive(True)
            self.state = GameState.READY
            self.next_round()

        else:
            raise ValueError("Invalid game state")

    def observe(self):
        return {
            "players": [p.observe() for p in self.players],
        }
        
    def to_json(self):
        return {
            "players": [p.to_json() for p in self.players],
            "state":{
                "round": self.round,
                "time": self.timer,
                "current_state": self.state.name,
                "state_time": self.state_time,
            }
        }
    
    def get_player_by_index(self, index):
        return self.players[index]
    
    def get_player_by_user_id(self, user_id):
        for player in self.players:
            if player.player_id == user_id:
                return player
        return None
    
    def get_winner():
        return None
    
    def step(self, frame: int):
        self.timer += 1 / frame
        
        if self.timer > self.state_time:
            self.timer = 0
            self.next_state()
        pass
        
    def stop(self):
        self.running = False
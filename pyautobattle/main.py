from src import *
from api.core import *
import json

def print_obs(obs: dict):
    print(json.dumps(obs, indent=4, sort_keys=True))

def wrap(obj: Base):
    print_obs(obj.observe())

def main():
    players = [Player(i, f"player_{i}") for i in range(8)]
    game = AutoBattlerGame(players=players, seed=42)
    register_unit(game, "data/unit.csv")
    refresh_shop(game, players[0])
    wrap(players[0])
    players[0].gold = 100
    print(0)
    
if __name__ == "__main__":
    main()
    
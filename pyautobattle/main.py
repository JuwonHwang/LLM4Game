from src import *
from api.core import *
import json

def print_obs(obs: dict):
    print(json.dumps(obs, indent=4, sort_keys=True))

def main():
    players = [Player(i, f"player_{i}") for i in range(8)]
    game = AutoBattlerGame(players=players, seed=42)
    result = get_shop(game, players[0])
    print(result)
    
if __name__ == "__main__":
    main()
    
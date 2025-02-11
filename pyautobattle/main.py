from src import *
from api.core import *
from api.battle import *
import json

def print_obs(obs: dict):
    print(json.dumps(obs, indent=4, sort_keys=True))

def wrap(obj: Base):
    print_obs(obj.observe())

def main():
    player_num = 8
    players = [Player(i, f"player_{i}") for i in range(player_num)]
    game = AutoBattlerGame(players=players, seed=42)
    register_unit(game, "data/unit.csv")
    # wrap(players[0])
    for i in range(player_num):
        refresh_shop(game, players[i])
        players[i].gold = 100
        purchase_unit(game, players[i], 0)
        bench_to_field(players[i], 0)
    result = combat(players[0], players[1])
    print(result)
    
if __name__ == "__main__":
    main()
    
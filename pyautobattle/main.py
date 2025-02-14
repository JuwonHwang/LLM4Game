from src import *
from api.core import *
from api.battle import *
import json
import sys
from src.render import *

def main():
    player_num = 8
    players = [Player(i, f"player_{i}") for i in range(player_num)]
    game = AutoBattlerGame(players=players, seed=42)
    register_unit(game, "data/unit.csv")
    # wrap(players[0])``
    for i in range(player_num):
        refresh_shop(game, players[i])
        players[i].gold = 100
        purchase_unit(game, players[i], 0)
        bench_to_field(players[i], 0)
    running = True
    player = players[0]
    action = None
    aux = dict()
    while running:
        # Event Handler
        render(game, player, action, aux)
        action = None
        aux = dict()
        command = input("COMMAND: ").split()
        try:
            if command[0] in ["quit"]:
                running = False
            elif command[0] in ["reroll", 'd']:
                action = "Reroll"
                reroll(game, player)
            elif command[0] in ['exp', 'f']:
                action = "BuyEXP"
                purchase_exp(player)
            elif command[0] in ['g', 'get', 'buy']:
                action = "BuyUnit"
                try:
                    index = int(command[1]) - 1
                    assert index in list(range(5))
                    purchased_unit = purchase_unit(game, player, index)
                    aux['unit'] = purchased_unit
                    if purchased_unit is None:
                        action = None
                except:
                    print("invalid command")
                    action = None
            elif command[0] in ['w', 'move']:
                if command[1] in ['b', 'bench']:
                    action = "B2F"
                    aux["unit"] = bench_to_field(player, int(command[2])-1)
                elif command[1] in ['f', 'field']:
                    action = "F2B"
                    aux["unit"] = field_to_bench(player, int(command[2])-1)
                else:
                    print("invalid move")
            elif command[0] in ['wb']:
                action = "B2F"
                aux["unit"] = bench_to_field(player, 0)
            elif command[0] in ['wf']:
                action = "F2B"
                aux["unit"] = field_to_bench(player, 0)
            elif command[0] in ['e', 'sell']:
                action = "SellUnit"
                aux["unit"] = sell_unit(game, player, int(command[1])-1)
            elif command[0] in ['s', 'swap']:
                action = "Swap"
                swap_unit(player, int(command[1])-1,int(command[2])-1)
            elif command[0] in ["money"]:
                player.gold += 100
            elif command[0] in ["wrap"]:
                if command[1] in ["game"]:
                    wrap(game)
                elif command[1] in ["player"]:
                    wrap(player)
        except Exception as e:
            action = None
            print("invalid command", e)
        # Mechanism
        


if __name__ == "__main__":
    main()
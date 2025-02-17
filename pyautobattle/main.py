from src import *
from api.core import *
from api.battle import *
import json
import sys
from src.render import *

def main():
    player_num = 8
    game = AutoBattlerGame("data/unit.csv", seed=42)
    for i in range(player_num):
        game.get_player_by_index(i).refresh_shop()
        game.get_player_by_index(i).gold = 100
        game.get_player_by_index(i).purchase_unit(0)
        game.get_player_by_index(i).bench_to_field(0)
    running = True
    player = game.get_player_by_index(0)
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
                player.reroll()
            elif command[0] in ['exp', 'f']:
                action = "BuyEXP"
                player.purchase_exp()
            elif command[0] in ['g', 'get', 'buy']:
                action = "BuyUnit"
                try:
                    index = int(command[1]) - 1
                    assert index in list(range(5))
                    purchased_unit = player.purchase_unit(index)
                    aux['unit'] = purchased_unit
                    if purchased_unit is None:
                        action = None
                except:
                    print("invalid command")
                    action = None
            elif command[0] in ['w', 'move']:
                if command[1] in ['b', 'bench']:
                    action = "B2F"
                    aux["unit"] = player.bench_to_field(int(command[2])-1)
                elif command[1] in ['f', 'field']:
                    action = "F2B"
                    aux["unit"] = player.field_to_bench(int(command[2])-1)
                else:
                    print("invalid move")
            elif command[0] in ['wb']:
                action = "B2F"
                aux["unit"] = player.bench_to_field(0)
            elif command[0] in ['wf']:
                action = "F2B"
                aux["unit"] = player.field_to_bench(0)
            elif command[0] in ['e', 'sell']:
                action = "SellUnit"
                aux["unit"] = player.sell_unit(int(command[1])-1)
            elif command[0] in ['s', 'swap']:
                action = "Swap"
                # swap_unit(player, int(command[1])-1,int(command[2])-1)
            elif command[0] in ["money"]:
                player.gold += 100
            elif command[0] in ["wrap"]:
                if command[1] in ["game"]:
                    wrap(game)
                elif command[1] in ["player"]:
                    wrap(player)
            elif command[0] in ["battle"]:
                assert command[1] != "1"
                combat_result = combat(player, game.get_player_by_index(i[int(command[1]) - 1]))
                print(combat_result["winner"], "win")
        except Exception as e:
            action = None
            print("invalid command", e)

if __name__ == "__main__":
    main()
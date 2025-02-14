from .color import *
from .player import Player
from api.core import *
import os

def render(game: AutoBattlerGame, p: Player, action: str, aux=None):
    # os.system("cls")
    if action == "Reroll":
        print(red("- Reroll -"))
    elif action == "BuyEXP":
        print(blue("- Buy EXP -"))
    elif action == "BuyUnit":
        print("You bought", aux["unit"])
    elif action == "B2F":
        print("You moved", aux["unit"], "from bench to field.")
    elif action == "F2B":
        print("You moved", aux["unit"], "from field to bench.")
    elif action == "SellUnit":
        print("You sold", aux["unit"])
    else:
        print()
    level_text = green(p.level)
    if p.level < 10:
        exp_text = blue(p.exp) + '/' + str(get_required_exp(p.level))
    else:
        exp_text = grey("MAX_LEVEL")
    rank = sorted(game.players, key=lambda _player: _player.hp)
    rank_text = ' | '.join([pl.name + " (" + red(max(pl.hp,0)) + ")" for pl in game.players])
    print(rank_text)
    print("================================================================================================================")
    print(p.field)
    print("================================================================================================================")
    print(p.bench)
    print("================================================================================================================")
    print("Level:", level_text, "EXP :", exp_text, "Gold :", Gold(p.gold))
    buy_exp_text = ' '.join([blue("(f)"), "Buy EXP", str(Gold(4)), ])
    reroll_text = ' '.join([red("(d)"), "Reroll", str(Gold(2))])
    buy_unit_text = ' '.join([green("(g #)"), "Buy Unit at #"])
    sell_unit_text = ' '.join([cyan("(e #)"), "Sell Unit at #"])
    move_unit_text = ' '.join([magenta("(w ? #)"), "Move Unit from ?", grey("(Bench or Field)"), "at #"])
    print(' | '.join([buy_unit_text, sell_unit_text, move_unit_text]))
    print(' | '.join([buy_exp_text, reroll_text]))
    print("================================================================================================================")
    appearance_rate_text = "Appearance rate : "+ ' | '.join([auto_color(f"Cost {i+1} (" + str(int(r*100))+ "%)", i+1) for i,r in enumerate(get_appearance_rate(p))])
    print(appearance_rate_text)
    print("================================================================================================================")
    print(p.shop)
    print("================================================================================================================")
from .color import *

CONTOUR = "================================================================================================================"

def render_lobby(data: dict):
    print('Game ID:', data['lobby']['game_id'])
    players = data['lobby']['players']
    print("========= LOBBY =========")
    for player in players:
        print(player)
    print("=========================")
    print("USER: ", data['home']['user']['user_id'])
    print("SCORE:", data['home']['user']['score'])
    print("=========================")
    
def render_home(data: dict):
    try:
        print("========= GAMES =========")
        if len(data['home']['games']) > 0:
            for game_id in data['home']['games']:
                print("GAME ID:", game_id)
        else:
            print("NO GAME")
        print("=========================")
        print("USER: ", data['home']['user']['user_id'])
        print("SCORE:", data['home']['user']['score'])
        print("=========================")
    except Exception as e:
        print(e)


def display_unit(unit):
    star = star_color(unit['level'])
    unit_name = auto_color(f"{unit['name']:12}", num=unit['cost'])
    return '[' + ' '.join([star, unit_name]) + ']'

def render_game(data: dict):
    game = data['game']['game'] 
    player = data['game']['player']
    level_text = green(player['level'])
    if player['level'] < 10:
        exp_text = blue(player['exp']) + '/' + str(player["req_exp"])
    else:
        exp_text = grey("MAX_LEVEL")
    rank = sorted(game["players"], key=lambda _player: _player["hp"])
    rank_text = '\n'.join([f"{r+1}: " + pl["name"] + " (" + red(max(pl["hp"],0)) + ")" for r, pl in enumerate(rank)])
    print(CONTOUR)
    print(rank_text)
    print(CONTOUR)
    print(player["field"])
    print(CONTOUR)
    print(player["bench"])
    print(CONTOUR)
    print("Level:", level_text, "EXP :", exp_text, "Gold :", Gold(player["gold"]))
    buy_exp_text = ' '.join([blue("(f)"), "Buy EXP", str(Gold(4)), ])
    reroll_text = ' '.join([red("(d)"), "Reroll", str(Gold(2))])
    buy_unit_text = ' '.join([green("(g #)"), "Buy Unit at #"])
    sell_unit_text = ' '.join([cyan("(e #)"), "Sell Unit at #"])
    move_unit_text = ' '.join([magenta("(w ? #)"), "Move Unit from ?", grey("(Bench or Field)"), "at #"])
    print(' | '.join([buy_unit_text, sell_unit_text, move_unit_text]))
    print(' | '.join([buy_exp_text, reroll_text]))
    print(CONTOUR)
    appearance_rate_text = "Appearance rate : "+ ' | '.join([auto_color(f"Cost {i+1} (" + str(int(r*100))+ "%)", i+1) for i,r in enumerate(player["unit_rate"])])
    print(appearance_rate_text)
    print(CONTOUR)
    print(player["shop"])
    print(CONTOUR)
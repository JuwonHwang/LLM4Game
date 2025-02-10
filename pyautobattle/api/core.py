from src import *
import random
import numpy as np

def get_appearance_rate(player: Player):
    if player.level <= 2:
        appearance_rate = [1.00, 0.00, 0.00, 0.00, 0.00]
    elif player.level == 3:
        appearance_rate = [0.75, 0.25, 0.00, 0.00, 0.00]
    elif player.level == 4:
        appearance_rate = [0.55, 0.30, 0.15, 0.00, 0.00]
    elif player.level == 5:
        appearance_rate = [0.45, 0.33, 0.20, 0.02, 0.00]
    elif player.level == 6:
        appearance_rate = [0.30, 0.40, 0.25, 0.05, 0.00]
    elif player.level == 7:
        appearance_rate = [0.19, 0.30, 0.40, 0.10, 0.01]
    elif player.level == 8:
        appearance_rate = [0.18, 0.25, 0.32, 0.22, 0.03]
    elif player.level == 9:
        appearance_rate = [0.15, 0.20, 0.25, 0.30, 0.10]
    elif player.level == 10:
        appearance_rate = [0.05, 0.10, 0.20, 0.40, 0.25]
    else:
        raise ValueError(f"Invalid level for player {player.player_id}")
    return appearance_rate

def get_shop(game: AutoBattlerGame, player: Player):
    appearance_rate = get_appearance_rate(player)
    chosen_costs = np.random.choice(
        np.arange(1,6),
        size=(5,),
        replace=True,
        p=appearance_rate
    )
    for cost in chosen_costs:
        pass
    return {}
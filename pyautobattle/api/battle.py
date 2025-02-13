from src import *
import random
import numpy as np
from .core import *
import csv
import json
import copy

def combat(player1: Player, player2: Player):
    home_field = copy.deepcopy(player1.field)
    away_field = copy.deepcopy(player2.field)
    winner = "home"
    # Combat phase
    timer = 0
    while timer < 3000:
        for pos, hu in enumerate(home_field.units):
            pass
        for pos, au in enumerate(away_field.units):
            pass
        timer += 1
        
    # Extended combat phase
    timer = 0
    while timer < 1500:
        timer += 1

    return {
        "winner": winner,
        "log": []
    }
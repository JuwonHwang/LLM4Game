from src import *
import random
import numpy as np
import csv
import json

def combat(player1: Player, player2: Player):
    field1 = player1.field.get_combat_mode()
    field2 = player2.field.get_combat_mode()
    
    # Combat phase
    timer = 0
    while timer < 3000:
        timer += 1
        
    # Extended combat phase
    timer = 0
    while timer < 1500:
        timer += 1
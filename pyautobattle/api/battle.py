from src import *
import random
import numpy as np
from .core import *
import csv
import json
import copy
import sys
import os
import time

def combat_render(home_player: Player, away_player: Player, result_list: list[dict]):
    if len(result_list) > 0:
        print(result_list)

def combat(home_player: Player, away_player: Player):
    home_field = copy.deepcopy(home_player.field)
    away_field = copy.deepcopy(away_player.field)
    winner = "home"
    # Combat phase
    timer = 0
    combat_time = 300_000_000
    log = []
    while timer < combat_time:
        result_list = []
        if len(home_field.units) <= 0 or len(away_field.units) <= 0 :
            if len(home_field.units) <= 0:
                winner = "away"
                damage = len(away_field)
            else:
                winner = "home"
                damage = len(home_field)
            break
        for pos, attacker in enumerate(home_field.units):
            attacker.update()
            if attacker.cooldown_time <= 0:
                attack_range = attacker.status.attackRange - pos
                for defender in away_field.units[:attack_range]:
                    result = attacker.hit(defender)
                    attacker.cooldown_time = attacker.status.attackSpeed
                    result_list.append(result)
                    if not defender.live:
                        away_field.units.remove(defender)
        for pos, attacker in enumerate(away_field.units):
            attacker.update()
            if attacker.cooldown_time <= 0:
                attack_range = defender.status.attackRange - pos
                for defender in home_field.units[:attack_range]:
                    result = attacker.hit(defender)
                    attacker.cooldown_time = attacker.status.attackSpeed
                    result_list.append(result)
                    if not defender.live:
                        home_field.units.remove(defender)
        # Extended combat phase
        # if timer < combat_time / 4:
        #     for hu in home_field.units:
        #         hu.status.attackSpeed -= 0.01
        #     for au in away_field.units:
        #         au.status.attackSpeed -= 0.001

        timer += 1
        time.sleep(0.001)
        combat_render(home_player, away_player, result_list)
        log.append(result_list)
        
    return {
        "winner": winner,
        "log": log,
        "damage": damage,
    }
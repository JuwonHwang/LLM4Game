from src import *
import random
import numpy as np
import csv
import json
import copy

def print_obs(obs: dict):
    print(json.dumps(obs, indent=4, sort_keys=True))

def wrap(obj: Base):
    print_obs(obj.observe())

def logger(t: str):
    print(t)

def register_unit(game: AutoBattlerGame, unit_csv_file_name: str):
    # Define the path to your CSV file
    file_path = unit_csv_file_name
    # Open and read the CSV file
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row["name"]
            cost = int(row["cost"])
            unit_status = Status(
                float(row["hp"]),
                float(row["mp"]),
                float(row["attack"]),
                float(row["defense"]),
                float(row["attackSpeed"]),
                float(row["specialAttack"]),
                float(row["specialDefense"]),
                float(row["criticalRate"]),
                float(row["criticalDamage"]),
                int(row["attackRange"]),
            )
            _unit = Unit(name, cost, 1, unit_status, [])
            game.units.append(_unit)
            game.unit_dict[name] = _unit
            count = game.unit_counts[cost]
            game.available_units[cost][name] = count

def get_appearance_rate(player: Player):
    if player.level == 1:
        appearance_rate = [1.00, 0.00, 0.00, 0.00, 0.00]
    elif player.level == 2:
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

def refresh_shop(game: AutoBattlerGame, player: Player):
    for u in player.shop.units:
        if u is None:
            continue
        unit_name, unit_level = u.name, u.level
        cost = game.unit_dict[unit_name].cost
        game.available_units[cost][unit_name] += 1 * (3 ** (unit_level - 1))
    player.shop.units = []
    appearance_rate = get_appearance_rate(player)
    chosen_costs = np.random.choice(
        np.arange(1, 6),
        size=(5,),
        replace=True,
        p=appearance_rate
    )
    for cost in chosen_costs:
        unit_pool = []
        for k,v in game.available_units[cost].items():
            for _ in range(v):
                unit_pool.append(k)
        chosen_unit = random.choice(unit_pool)
        game.available_units[cost][chosen_unit] -= 1
        player.shop.units.append(game.unit_dict[chosen_unit])

def reroll(game: AutoBattlerGame, player: Player):
    if player.gold < 2:
        logger(f"{player.name} has not enough gold to reroll.")
    else:
        player.gold -= 2
        refresh_shop(game, player)
        logger(f"{player.name} rerolled.")

def upgrade(player: Player, unit_name: str, unit_level: int):
    bench_count = player.bench.count(unit_name, unit_level) 
    field_count = player.field.count(unit_name, unit_level) 
    if bench_count + field_count < 3:
        return None, None
    if bench_count == 1:
        player.bench.remove(unit_name, unit_level)
        player.field.remove(unit_name, unit_level)
        player.field.remove(unit_name, unit_level)
    elif bench_count == 2:
        player.bench.remove(unit_name, unit_level)
        player.bench.remove(unit_name, unit_level)
        player.field.remove(unit_name, unit_level)
    elif bench_count == 3:
        player.bench.remove(unit_name, unit_level)
        player.bench.remove(unit_name, unit_level)
        player.bench.remove(unit_name, unit_level)
    return unit_name, unit_level + 1

def get_unit(game: AutoBattlerGame, unit_name: str, unit_level: int):
    _unit = copy.deepcopy(game.unit_dict[unit_name])
    _unit.level = unit_level
    _unit.status = Status(
        hp=_unit.status.hp * 1.6,
        mp=_unit.status.mp,
        attack= _unit.status.attack * 1.6,
        defense= _unit.status.defense * 1.6,
        attackSpeed= _unit.status.attackSpeed,
        specialAttack= _unit.status.specialAttack,
        specialDefense= _unit.status.specialDefense * 1.6,
        criticalRate= _unit.status.criticalRate,
        criticalDamage= _unit.status.criticalDamage,
        attackRange= _unit.status.attackRange
    )
    return _unit

def purchase_unit(game: AutoBattlerGame, player: Player, shop_idx: int):
    if player.shop.units[shop_idx] is None:
        logger(f"{player.name} tried to buy None.")
        return None
    unit_name = player.shop.units[shop_idx].name
    purchased_unit = copy.deepcopy(game.unit_dict[unit_name])
    if player.gold < purchased_unit.cost:
        logger(f"{player.name} does not have enough gold.")
        return None
    player.bench.units.append(purchased_unit)
    for i in range(1,4):
        upgrade_name, upgrade_level = upgrade(player, purchased_unit.name, unit_level=i)
        if upgrade_name is not None:
            if not player.field.is_full():
                player.field.units.append(get_unit(game, upgrade_name, upgrade_level))
            else:
                player.bench.units.append(get_unit(game, upgrade_name, upgrade_level))
            logger(" ".join([player.name, "upgraded", upgrade_name, "to level", str(upgrade_level)]))
    if len(player.bench.units) > player.bench.max_units:
        logger(f"{player.name} does not have enough bench room.")
        player.bench.units.pop()
        return None
    else:
        player.shop.units[shop_idx] = None
        player.gold -= purchased_unit.cost
        logger(f"{player.name} purchased {unit_name}.")
        return purchased_unit
    
def sell_unit(game: AutoBattlerGame, player: Player, bench_idx: int):
    if len(player.bench.units) <= bench_idx or player.bench.units[bench_idx] is None:
        logger(f"{player.name} does not have unit at bench index {bench_idx}.")
        return None
    else:
        _unit = player.bench.units.pop(bench_idx)
        earn_gold = _unit.cost * (3 ** (_unit.level - 1)) - 1 if _unit.level > 1 else _unit.cost
        player.gold += earn_gold
        game.available_units[_unit.cost][_unit.name] += 3 ** (_unit.level - 1)
        logger(f"{player.name} selled level {_unit.level} - {_unit.name}, earned {earn_gold} gold.")
        return _unit
        
def bench_to_field(player: Player, bench_idx: int):
    if len(player.bench.units) <= bench_idx or player.bench.units[bench_idx] is None:
        logger(f"{player.name} does not have unit at {bench_idx} of bench.")
    elif len(player.field.units) >= player.field.max_units:
        logger(f"{player.name}'s field is full.")
    else:
        _unit = player.bench.units.pop(bench_idx)
        player.field.units.append(_unit)
        logger(f"{player.name} moved {_unit.name} from bench index {bench_idx} to field.")
        return _unit
    return None

def field_to_bench(player: Player, field_idx: int):
    if len(player.field.units) <= field_idx or player.field.units[field_idx] is None:
        logger(f"{player.name} does not have unit at field index {field_idx}.")
    elif len(player.bench.units) >= player.bench.max_units:
        logger(f"{player.name}'s bench is full.")
    else:
        _unit = player.field.units.pop(field_idx)
        player.bench.units.append(_unit)
        logger(f"{player.name} moved {_unit.name} from field index {field_idx} to bench.")
        return _unit
    return None

def get_required_exp(level: int):
    EXP_LIST = [0,2,2,6,10,20,36,48,76,84, float("inf")]
    return EXP_LIST[level]

def player_level_up(player: Player):
    required_exp = get_required_exp(player.level)
    player.exp -= required_exp
    player.field.max_units += 1
    player.level += 1
    logger(f"{player.name}'s level up to level {player.level}")

def purchase_exp(player: Player):
    if player.level >= 10:
        logger(f"{player.name}'s level is max.")
    elif player.gold < 4:
        logger(f"{player.name}'s gold is not enough to buy EXP.")
    else:
        player.gold -= 4
        player.exp += 4
        logger(f"{player.name} purchased 4 EXP.")
        while player.level < 10 and player.exp >= get_required_exp(player.level):
            player_level_up(player)
        
def give_exp(player: Player, exp_amount: int):
    if player.level >= 10:
        logger(f"{player.name}'s level is max.")
    else:
        player.exp += exp_amount
        while player.level < 10 and player.exp >= get_required_exp(player.level):
            player_level_up(player)
            
def swap_unit(player: Player, index1:int, index2:int):
    pass
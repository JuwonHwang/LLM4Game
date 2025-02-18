from .base import Base
from .bench import Bench
from .shop import Shop
from .field import Field
from .pool import Pool
import numpy as np
import random
import copy

class Player(Base):
    def __init__(self, player_id, name, pool):
        self.player_id = player_id
        self.name = name
        self.hp = 100
        self.field = Field()
        self.bench = Bench()
        self.shop = Shop()
        self.pool : Pool = pool
        self.gold = 0
        self.level = 1
        self.exp = 0
        self.req_exp_list = [0,2,2,6,10,20,36,48,76,84, float("inf")]
        self.streak = 0
        
    def observe(self):
        return {
            "id": self.player_id,
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "field": self.field.observe(),
            "bench": self.bench.observe(),
            "shop": self.shop.observe(),
            "gold": self.gold,
            "exp": self.exp,
            "req_exp": self.get_required_exp(),
            "unit_rate": self.get_appearance_rate(),
            "streak": self.streak
        }
    
    def get_required_exp(self):
        return self.req_exp_list[self.level]

    def player_level_up(self):
        required_exp = self.get_required_exp()
        self.exp -= required_exp
        self.field.max_units += 1
        self.level += 1
        print(f"{self.name}'s level up to level {self.level}")

    def purchase_exp(self):
        if self.level >= 10:
            print(f"{self.name}'s level is max.")
        elif self.gold < 4:
            print(f"{self.name}'s gold is not enough to buy EXP.")
        else:
            self.gold -= 4
            self.exp += 4
            print(f"{self.name} purchased 4 EXP.")
            while self.level < 10 and self.exp >= self.get_required_exp():
                self.player_level_up()
            
    def give_exp(self, exp_amount: int):
        if self.level >= 10:
            print(f"{self.name}'s level is max.")
        else:
            self.exp += exp_amount
            while self.level < 10 and self.exp >= self.get_required_exp():
                self.player_level_up()

    def bench_to_field(self, bench_idx: int):
        if len(self.bench.units) <= bench_idx or self.bench.units[bench_idx] is None:
            print(f"{self.name} does not have unit at {bench_idx} of bench.")
        elif len(self.field.units) >= self.field.max_units:
            print(f"{self.name}'s field is full.")
        else:
            _unit = self.bench.units.pop(bench_idx)
            self.field.units.append(_unit)
            print(f"{self.name} moved {_unit.name} from bench index {bench_idx} to field.")
            return _unit
        return None

    def field_to_bench(self, field_idx: int):
        if len(self.field.units) <= field_idx or self.field.units[field_idx] is None:
            print(f"{self.name} does not have unit at field index {field_idx}.")
        elif len(self.bench.units) >= self.bench.max_units:
            print(f"{self.name}'s bench is full.")
        else:
            _unit = self.field.units.pop(field_idx)
            self.bench.units.append(_unit)
            print(f"{self.name} moved {_unit.name} from field index {field_idx} to bench.")
            return _unit
        return None
    
    def upgrade(self, unit_name: str, unit_level: int):
        bench_count = self.bench.count(unit_name, unit_level) 
        field_count = self.field.count(unit_name, unit_level) 
        if bench_count + field_count < 3:
            return None, None
        if bench_count == 0:
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
        elif bench_count == 1:
            self.bench.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
        elif bench_count == 2:
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
        elif bench_count == 3:
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
        return unit_name, unit_level + 1

    def reroll(self):
        if self.gold < 2:
            print(f"{self.name} has not enough gold to reroll.")
        else:
            self.gold -= 2
            self.refresh_shop()
            print(f"{self.name} rerolled.")

    def get_appearance_rate(self):
        if self.level == 1:
            appearance_rate = [1.00, 0.00, 0.00, 0.00, 0.00]
        elif self.level == 2:
            appearance_rate = [1.00, 0.00, 0.00, 0.00, 0.00]
        elif self.level == 3:
            appearance_rate = [0.75, 0.25, 0.00, 0.00, 0.00]
        elif self.level == 4:
            appearance_rate = [0.55, 0.30, 0.15, 0.00, 0.00]
        elif self.level == 5:
            appearance_rate = [0.45, 0.33, 0.20, 0.02, 0.00]
        elif self.level == 6:
            appearance_rate = [0.30, 0.40, 0.25, 0.05, 0.00]
        elif self.level == 7:
            appearance_rate = [0.19, 0.30, 0.40, 0.10, 0.01]
        elif self.level == 8:
            appearance_rate = [0.18, 0.25, 0.32, 0.22, 0.03]
        elif self.level == 9:
            appearance_rate = [0.15, 0.20, 0.25, 0.30, 0.10]
        elif self.level == 10:
            appearance_rate = [0.05, 0.10, 0.20, 0.40, 0.25]
        return appearance_rate
    
    def get_turn_gold(self):
        interest = min(self.gold % 10, 5)
        streak_gold = 0
        if abs(self.streak) >= 2: 
            streak_gold += 1
        if abs(self.streak) >= 4:
            streak_gold += 1
        if abs(self.streak) >= 6:
            streak_gold += 1
        self.gold += interest + streak_gold
    
    def get_turn_exp(self):
        self.give_exp(2)

    def refresh_shop(self):
        for u in self.shop.units:
            if u is None:
                continue
            self.pool.add_unit(u)
        self.shop.clear()
        appearance_rate = self.get_appearance_rate()
        chosen_costs = np.random.choice(
            np.arange(1, 6),
            size=(5,),
            replace=True,
            p=appearance_rate
        )
        for cost in chosen_costs:
            unit_pool = []
            for k,v in self.pool.available_units[cost].items():
                for _ in range(v):
                    unit_pool.append(k)
            chosen_unit = random.choice(unit_pool)
            self.pool.remove_unit(self.pool.unit_dict[chosen_unit])
            self.shop.units.append(self.pool.unit_dict[chosen_unit])

    def purchase_unit(self, shop_idx: int):
        if self.shop.units[shop_idx] is None:
            print(f"{self.name} tried to buy None.")
            return None
        unit_name = self.shop.units[shop_idx].name
        purchased_unit = copy.deepcopy(self.pool.unit_dict[unit_name])
        if self.gold < purchased_unit.cost:
            print(f"{self.name} does not have enough gold.")
            return None
        self.bench.units.append(purchased_unit)
        for i in range(1,4):
            upgrade_name, upgrade_level = self.upgrade(purchased_unit.name, unit_level=i)
            if upgrade_name is not None:
                if not self.field.is_full():
                    self.field.units.append(self.pool.get_unit(upgrade_name, upgrade_level))
                else:
                    self.bench.units.append(self.pool.get_unit(upgrade_name, upgrade_level))
                print(" ".join([self.name, "upgraded", upgrade_name, "to level", str(upgrade_level)]))
        if len(self.bench.units) > self.bench.max_units:
            print(f"{self.name} does not have enough bench room.")
            self.bench.units.pop()
            return None
        else:
            self.shop.units[shop_idx] = None
            self.gold -= purchased_unit.cost
            print(f"{self.name} purchased {unit_name}.")
            return purchased_unit
        
    def sell_unit(self, bench_idx: int):
        if len(self.bench.units) <= bench_idx or self.bench.units[bench_idx] is None:
            print(f"{self.name} does not have unit at bench index {bench_idx}.")
            return None
        else:
            _unit = self.bench.units.pop(bench_idx)
            earn_gold = _unit.get_sell_gold()
            self.gold += earn_gold
            self.pool.add_unit(_unit)
            print(f"{self.name} selled level {_unit.level} - {_unit.name}, earned {earn_gold} gold.")
            return _unit
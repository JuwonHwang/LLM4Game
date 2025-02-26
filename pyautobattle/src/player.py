from .unit import Unit
from .base import Base
from .bench import Bench
from .shop import Shop
from .field import Field
from .pool import Pool
import numpy as np
import random
import copy

MSG = 'message'
ERROR = 'error'

class Player(Base):
    def __init__(self, player_id, name, pool):
        self.player_id = player_id
        self.name = name
        self.hp = 2
        self.field = Field()
        self.bench = Bench()
        self.shop = Shop()
        self.pool : Pool = pool
        self.gold = 0
        self.level = 1
        self.exp = 0
        self.req_exp_list = [0,2,2,6,10,20,36,48,76,84, float("inf")]
        self.streak = 0
        self.active = False
        
    def is_alive(self):
        return self.hp > 0
    
    def get_damage(self, amount):
        self.hp -= amount
        
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
        
    def to_json(self):
        return {
            "id": self.player_id,
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "field": self.field.to_json(),
            "bench": self.bench.to_json(),
            "shop": self.shop.to_json(),
            "gold": self.gold,
            "exp": self.exp,
            "req_exp": self.get_required_exp(),
            "unit_rate": self.get_appearance_rate(),
            "streak": self.streak,
            "active": self.active,
        }
    
    def get_required_exp(self):
        return self.req_exp_list[self.level]

    def player_level_up(self):
        required_exp = self.get_required_exp()
        self.exp -= required_exp
        self.field.level_up()
        self.level += 1
        return f"{self.name} level up to {self.level}"

    def purchase_exp(self):
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        if self.level >= 10:
            return {
                MSG: [f"{self.name}'s level is max"]
            }
        elif self.gold < 4:
            return {
                MSG: [f"{self.name}'s gold is not enough to buy EXP"]
            }
        else:
            self.gold -= 4
            self.exp += 4
            messages = [f"{self.name} buy EXP"]
            while self.level < 10 and self.exp >= self.get_required_exp():
                messages.append(self.player_level_up())
            return {
                MSG: messages
            }
            
    def give_exp(self, exp_amount: int):
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        if self.level >= 10:
            return {
                MSG: [f"{self.name}'s level is max"]
            }
        else:
            self.exp += exp_amount
            messages = [f"{self.name} get {exp_amount} EXP"]
            while self.level < 10 and self.exp >= self.get_required_exp():
                messages.append(self.player_level_up())
            return {
                MSG: messages
            }

    def swap(self, where: list[Unit], src_idx: int, trgt_idx: int):
        if src_idx > trgt_idx:
            _unit = where.pop(src_idx)
            where.insert(trgt_idx, _unit)
        elif src_idx < trgt_idx:
            _unit = where.pop(src_idx)
            where.insert(trgt_idx - 1, _unit)
        else:
            pass

    def move_unit(self, source_type: str, target_type: str, src_idx: int, trgt_idx: int):
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        source = None
        target = None
        if source_type in ['bench', 'b']:
            source_type = 'bench'
            source:Bench = self.bench
        else:
            source_type = 'field'
            source:Field = self.field
        if target_type in ['bench', 'b']:
            target_type = 'bench'
            target:Bench = self.bench
        else:
            target_type = 'field'
            target:Field = self.field
        if src_idx > source.num_slots or trgt_idx > target.num_slots:
            return {
                MSG: [f"{self.name} tried invalid pop or insert"]
            }
        elif src_idx < 0:
            return {
                MSG: [f"{self.name} tried invalid pop or insert"]
            }
        try:
            source_unit = source.pop(src_idx)
            if source_unit is None:
                return {
                    MSG: [f"{self.name} tried to move none"]
                }
            target_unit = target.pop(trgt_idx)
            if trgt_idx == -1:
                if target_type == source_type:
                    source.units[src_idx] = source_unit
                    return {
                        MSG: [f"{self.name} invalid move"]
                    }
                trgt_idx = target.find_empty()
            if src_idx == trgt_idx and source_type == target_type:
                source.units[src_idx] = source_unit
                return {
                    MSG: [f"{self.name} move same position"]
                }
            elif target.is_full():
                source.units[src_idx] = source_unit
                target.units[trgt_idx] = target_unit
                return {
                    MSG: [f"{self.name} {target_type} is full"]
                }
            target.units[trgt_idx] = source_unit
            source.units[src_idx] = target_unit
            return {
                MSG: [f"{self.name} moved {source_unit.name} ({source_type},{src_idx}) <-> {target_unit.name if target_unit is not None else None} ({target_type},{trgt_idx})"]
            }
        except Exception as e:
            return {
                MSG: [f"{self.name} move failed due to an unknown reason"]
            }
    
    def upgrade(self, unit_name: str, unit_level: int):
        bench_count = self.bench.count(unit_name, unit_level) 
        field_count = self.field.count(unit_name, unit_level) 
        if bench_count + field_count < 3:
            return None, None
        if bench_count == 0:
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.add(self.pool.get_unit(unit_name, unit_level+1))
        elif bench_count == 1:
            self.bench.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.add(self.pool.get_unit(unit_name, unit_level+1))
        elif bench_count == 2:
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
            self.field.remove(unit_name, unit_level)
            self.field.add(self.pool.get_unit(unit_name, unit_level+1))
        elif bench_count == 3:
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
            self.bench.remove(unit_name, unit_level)
            self.bench.add(self.pool.get_unit(unit_name, unit_level+1))
        return unit_name, unit_level + 1
    
    def reroll(self):
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        if self.gold < 2:
            return {
                MSG: [f"{self.name} has not enough gold to reroll"]
            }
        else:
            self.gold -= 2
            self.refresh_shop()
            return {
                MSG: [f"{self.name} reroll"]
            }

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
    
    def get_turn_gold(self, turn):
        turn_gold = 1
        if turn < 5:
            turn_gold += 4
        else:
            turn_gold += turn // 5
        interest = min(self.gold % 10, 5)
        streak_gold = 0
        if abs(self.streak) >= 2: 
            streak_gold += 1
        if abs(self.streak) >= 4:
            streak_gold += 1
        if abs(self.streak) >= 6:
            streak_gold += 1
        self.gold += interest + streak_gold + turn_gold
    
    def win(self):
        self.gold += 1
        if self.streak < 0:
            self.streak = 1
        else:
            self.streak += 1
    
    def lose(self):
        if self.streak > 0:
            self.streak = -1
        else:
            self.streak -= 1
    
    def draw(self):
        self.streak = 0
    
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
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        if self.shop.units[shop_idx] is None:
            return {
                MSG: [f"{self.name} tried to buy invalid index in shop"]
            }
        unit_name = self.shop.units[shop_idx].name
        purchased_unit = copy.deepcopy(self.pool.unit_dict[unit_name])
        if self.gold < purchased_unit.cost:
            return {
                MSG: [f"{self.name} does not have enough gold"]
            }
        messages = []
        index = self.bench.add(purchased_unit)
        messages.append(f"{self.name} try to buy {unit_name}.")
        if index == -1:
            if self.bench.count(unit_name, 1) + self.field.count(unit_name, 1) >= 2:
                if self.bench.count(unit_name, 1) >= 2:
                    self.bench.remove(unit_name,1)
                    self.bench.remove(unit_name,1)
                    self.bench.add(self.pool.get_unit(unit_name, 2))
                elif self.bench.count == 1:
                    self.bench.remove(unit_name,1)
                    self.field.remove(unit_name,1)
                    self.field.add(self.pool.get_unit(unit_name, 2))
                else:
                    self.field.remove(unit_name,1)
                    self.field.remove(unit_name,1)
                    self.field.add(self.pool.get_unit(unit_name, 2))
                messages.append(f"{self.name} upgrade {unit_name} to level 2")
            else:
                return {
                    MSG: [f"{self.name} does not have enough bench room."]
                }
        self.gold -= purchased_unit.cost
        self.shop.units[shop_idx] = None
        for i in range(1,4):
            upgrade_name, upgrade_level = self.upgrade(purchased_unit.name, unit_level=i)
            if upgrade_name is not None:
                messages.append(f"{self.name} upgrade {upgrade_name} to level {upgrade_level}")
        messages.append(f"{self.name} successfully bought {unit_name}.")
        return {
            MSG: messages
        }
        
    def sell_unit(self, source_type, index: int):
        if not self.is_alive():
            return {
                MSG: [f"{self.name} is not alive"]
            }
        source = None
        if source_type in ['bench', 'b']:
            source = self.bench
        else:
            source = self.field
        if source.units[index] is None:
            return {
                MSG: [f"{self.name} does not have unit at {source_type} index {index}."]
            }
        else:
            _unit = source.pop(index)
            earn_gold = _unit.get_sell_gold()
            self.gold += earn_gold
            self.pool.add_unit(_unit)
            return {
                MSG: [f"{self.name} selled level {_unit.level} - {_unit.name}, earned {earn_gold} gold."]
            }
    
    def add_gold(self, amount: int):
        self.gold += int(amount)
        return {
                MSG: [f"{self.name} gold + 100."]
        }
        
    def play_randomly(self):
        pass
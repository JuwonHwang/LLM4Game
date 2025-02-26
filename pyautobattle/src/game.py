from .base import Base
from .player import Player
from .pool import Pool
from .unit import Unit
import time
from enum import Enum
import random
import copy
from .util import TEAM, astar

ROW = 8
COL = 7

class GameState(Enum):
    READY = "ready"
    BATTLE = "battle"
        
class BattleState(Enum):
    WIN = 'win'
    LOSE = 'lose'
    DRAW = 'draw'
    INBATTLE = 'inbattle'
        
class AutoBattlerGame(Base):
    def __init__(self, game_id, unit_file='pyautobattle/data/unit.csv', synergy_file='pyautobattle/data/synergy.json', seed=0):
        self.game_id = game_id
        self.seed = seed
        self.pool = Pool(unit_file, synergy_file)
        self.round = 0
        self.timer = 0
        self.state_time = 10
        self.winner = None
        self.players: list[Player] = []
        self.current_players = set()
        self.running = False
        self.matchup = None
        self.arena = []
        self.state = GameState.READY
        self.battle_state = {}

    def register(self, user_id):
        self.current_players.add(user_id)

    def quit(self, user_id):
        self.current_players.discard(user_id)
        return len(self.current_players)

    def start(self):
        for user_id in list(self.current_players):
            self.players.append(Player(user_id, f"{user_id}", pool=self.pool))
        while len(self.players) < 8:
            i = len(self.players)
            self.players.append(Player(f"{self.game_id}-{i}", f"{self.game_id}-{i}", pool=self.pool))
        for player in self.players:
            player.gold = 100
            player.bench.add(self.pool.sample(1))
        for player in self.players:
            player.refresh_shop()
        self.running = True
        self.setActive(True)

    def next_round(self):
        for player in self.players:
            player.refresh_shop()
            player.get_turn_exp()
            player.get_turn_gold()
        self.round += 1

    def setActive(self, value=True):
        for player in self.players:
            player.active = value

    def next_state(self):
        if self.state == GameState.READY: # READY -> BATTLE
            self.setActive(False)
            self.state = GameState.BATTLE
            self.state_time = 15
            self.force_placement()
            self.start_battle()
        elif self.state == GameState.BATTLE: # BATTLE -> READY
            self.setActive(True)
            self.state = GameState.READY
            self.next_round()
            self.state_time = 15
        else:
            raise ValueError("Invalid game state")

    def observe(self):
        return {
            "players": [p.observe() for p in self.players],
        }
        
    def to_json(self):
        return {
            "players": [p.to_json() for p in self.players],
            "state":{
                "round": self.round,
                "time": self.timer,
                "current_state": self.state.name,
                "state_time": self.state_time,
            },
            "battle": self.battle_to_json(),
        }
    
    def get_player_by_index(self, index):
        return self.players[index]
    
    def get_player_by_user_id(self, user_id):
        for player in self.players:
            if player.player_id == user_id:
                return player
        return None
    
    def get_winner():
        return None
    
    def step(self, frame: int):
        self.check_end()
        self.timer += 1 / frame
        
        if self.state == GameState.BATTLE and self.matchup and self.arena:
            for i, _arena in enumerate(self.arena):
                self.step_battle(_arena)
                
        if self.timer > self.state_time:
            self.timer = 0
            self.next_state()
            
    def check_end(self):
        live_players = self.get_live_players()
        if len(live_players) > 1:
            return False
        else:
            self.stop()
            return True
        
    def stop(self):
        self.running = False
        
    def get_live_players(self):
        return [player for player in self.players if player.is_alive()]
        
    def force_placement(self):
        live_players = self.get_live_players()
        for player in live_players:
            for i, unit in enumerate(player.bench):
                if player.field.is_full():
                    break
                if unit is not None:
                    player.move_unit('bench', 'field', i, -1)
        
    def start_battle(self):
        def _make_pair():
            live_players = self.get_live_players()
            random.shuffle(live_players)
            if len(live_players) % 2:
                live_players.append(live_players[0])
            pair_players = list(zip(live_players[::2], live_players[1::2]))
            return pair_players
        
        self.matchup = _make_pair()
        self.arena = []
        self.battle_state = {}
        for home_player, away_player in self.matchup:
            # print(home_player.name, away_player.name)
            self.arena.append(self.set_arena(copy.deepcopy(home_player.field), copy.deepcopy(away_player.field)))
            self.battle_state[home_player.player_id] = BattleState.INBATTLE
            self.battle_state[away_player.player_id] = BattleState.INBATTLE
            
    def set_arena(self, home_field, away_field):
        _arena = []
        
        def _index_to_position(where, i):
            if where == TEAM.HOME:
                return [i // COL, i % COL]
            else:
                return [7 - i // COL, 6 - i % COL]
        
        for i, unit in enumerate(home_field):
            if unit is not None:
                unit.team = TEAM.HOME
                _arena.append({'unit':unit, 'pos':_index_to_position(TEAM.HOME, i)})
        for i, unit in enumerate(away_field):
            if unit is not None:
                unit.team = TEAM.AWAY
                _arena.append({'unit':unit, 'pos':_index_to_position(TEAM.AWAY, i)})
        
        # print(_arena)
        return _arena
        
    def battle_to_json(self):
        battles = {}
        if self.matchup and self.arena:
            for (home_player, away_player), _arena in zip(self.matchup, self.arena):
                v = [{'unit': u['unit'].to_json(), 'pos': u['pos']} for u in _arena]
                battles[home_player.player_id] = {
                    'team': TEAM.HOME.value,
                    'arena': v,
                    'state': self.battle_state[home_player.player_id].value
                }
                battles[away_player.player_id] = {
                    'team': TEAM.AWAY.value,
                    'arena': v,
                    'state': self.battle_state[away_player.player_id].value
                }
        else:
            for player in self.players:
                battles[player.player_id] = None
        return battles
        
    def step_battle(self, _arena):
        def norm(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        def find_nearest_enemy(pos, team, unit_dict_list):
            nearest_index = -1
            nearest_dist = 999999
            for i, unit_dict in enumerate(unit_dict_list):
                if unit_dict['pos'] == pos:
                    continue
                dist = norm(unit_dict['pos'], pos)
                if dist < nearest_dist and team != unit_dict['unit'].team:
                    nearest_dist = dist
                    nearest_index = i
            try:
                return nearest_index, unit_dict_list[nearest_index]['unit'], unit_dict_list[nearest_index]['pos']
            except:
                return nearest_index, None, None
        
        for unit_info_i in _arena:
            unit_i: Unit = unit_info_i['unit']
            pos_i = unit_info_i['pos']
            unit_i.update()
            target_index, target_unit, target_pos = find_nearest_enemy(pos_i, unit_i.team, _arena)
            if target_index == -1:
                return
            if norm(target_pos, pos_i) <= unit_i.status.attackRange: # attack!
                if unit_i.alive() and unit_i.cooldowned():
                    unit_i.hit(target_unit)
            else:
                if unit_i.alive() and unit_i.move():
                    obstacles = [unit_info['pos'] for unit_info in _arena]
                    path, direction = astar(pos_i, target_pos, obstacles)
                    if direction is not None:
                        pos_i[0] += direction[0][0]
                        pos_i[1] += direction[0][1]
        i = 0     
        while i < len(_arena):
            if _arena[i]['unit'].alive():
                i += 1
            else:
                _arena.pop(i)
                
    def end_battle(self):
        
        def who_win(_arena):
            team_list = [u['unit'].team for u in _arena]
            check_home = TEAM.HOME in team_list
            check_away = TEAM.AWAY in team_list
            if check_home and check_away:
                return BattleState.DRAW, BattleState.DRAW
            elif check_home:
                return BattleState.WIN, BattleState.LOSE
            elif check_away:
                return BattleState.LOSE, BattleState.WIN
            else:
                return BattleState.DRAW, BattleState.DRAW
                
        for i, _arena in enumerate(self.arena):
            home_state, away_state = who_win(_arena)
            self.battle_state[self.matchup[i][0].player_id] = home_state
            self.battle_state[self.matchup[i][1].player_id] = away_state
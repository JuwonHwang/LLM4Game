import os
import json
import logging
import socketio
from aiohttp import web
from pyautobattle.src import AutoBattlerGame
import asyncio
from datetime import datetime

# Setup logging
LOG_DIR = 'log'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'server.log')
logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE, format='%(asctime)s, %(name)s, %(levelname)s, %(message)s')
logger = logging.getLogger('game_server')

class GameServer:
    def __init__(self):
        self.user_db_path = './db/user.json'
        self.replay_path = './replay'
        self.load_user_db()
        
        self.sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True, access_log=logger)
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.clients = set()
        self.sid_to_user = {}
        self.games = {}
        self.rooms = {}
        
        self.register_events()
    
    def register_events(self):
        events = {
            'connect': self.connect,
            'disconnect': self.disconnect,
            'login': self.login,
            'register_game': self.register_game,
            'start_game': self.start_game,
            'quit_game': self.quit_game,
            'reroll': self.reroll,
            'buy_exp': self.buy_exp,
            'buy_unit': self.buy_unit,
            'sell_unit': self.sell_unit,
            'move_unit': self.move_unit,
            'money': self.money,
        }
        for event, handler in events.items():
            self.sio.event(handler)

    def load_user_db(self):
        if os.path.exists(self.user_db_path):
            with open(self.user_db_path, 'r', encoding='utf-8') as file:
                self.user_info = json.load(file)
                print("user_file loaded")
        else:
            self.user_info = {}
    
    async def log(self, subject, message):
        logger.info(f"{subject}: {message}")
        print(f"{subject}: {message}")

    async def connect(self, sid, environ):
        self.clients.add(sid)
        await self.log(sid, "Connected")
    
    async def disconnect(self, sid):
        game_id = await self.get_game_id(sid)
        if game_id and game_id in self.games.keys():
            await self.send_lobby_state(game_id)
            
        await self.quit_game(sid)
        self.clients.discard(sid)
        
        await self.log(sid, "Disconnected")
    
    async def login(self, sid, user_id):
        user_id = user_id[0] if isinstance(user_id, list) else user_id
        self.sid_to_user[sid] = user_id
        
        if user_id not in self.user_info.keys():
            self.user_info[user_id] = {'user_id': user_id, 'score': 100, 'playing': False, 'game_id': None, 'match_results': []}
            self.save_user_db()
            await self.log(sid, f'User {user_id} created')
        else:
            self.user_info[user_id]['playing'] = False
            self.user_info[user_id]['game_id'] = None
        
        await self.log(sid, f'User {user_id} logged in')
        await self.send_user_state(sid)
        await self.send_home_state()
        return True
    
    def save_user_db(self):
        with open(self.user_db_path, 'w', encoding='utf-8') as file:
            json.dump(self.user_info, file, indent=4, ensure_ascii=False)
    
    async def register_game(self, sid, game_id=None):
        if game_id == None:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            game_id = current_time
        user_id = await self.get_user_id(sid)
        await self.sio.emit('response', f'Your ID {user_id}', to=sid)
        
        if not user_id:
            await self.sio.emit('response', 'You must log in before registering a game', to=sid)
            return False

        if self.user_info[user_id]['game_id'] is not None:
            await self.sio.emit('response', 'You cannot register more than one game', to=sid)
            return False
        
        if game_id not in self.games.keys():
            self.games[game_id] = AutoBattlerGame(game_id)
            self.rooms[game_id] = []
            await self.log(sid, f'Game {game_id} created')
            await self.sio.emit('response', f'Game {game_id} created', to=sid)
        elif self.games[game_id].running:
            await self.sio.emit('response', 'The game is already started', to=sid)
            return False
        game = self.games[game_id]
        game.register(user_id)
        self.rooms[game_id].append(sid)
        self.user_info[user_id]['game_id'] = game_id
        await self.send_user_state(sid)
        if len(game.current_players) > 8:
            await self.sio.emit('response', 'ERROR: Max # of players reached', to=sid)
            return False
        else:
            await self.sio.emit('response', f'You joined {game_id}', to=sid)
            await self.send_lobby_state(game_id)
            await self.send_home_state()
            if len(game.current_players) == 8:
                if not game.running:
                    game.start()
                    asyncio.create_task(self.run_battle(game_id))
                    await self.send_game_state(game_id)
                    await self.send_home_state()
                    await self.log(sid, f"game {game_id} start")
                else:
                    await self.log(sid, f"game {game_id} aleady started")
            return True
    
    async def start_game(self, sid, game_id=None):
        user_id = await self.get_user_id(sid)
        game_id = game_id if user_id == 'ADMIN' else await self.get_game_id(sid)

        if game_id and game_id in self.games.keys():
            if not self.games[game_id].running:
                self.games[game_id].start()
                asyncio.create_task(self.run_battle(game_id))
                await self.send_game_state(game_id)
                await self.send_home_state()
                await self.log(sid, f"game {game_id} start")
            else:
                await self.log(sid, f"game {game_id} already start")
            return True
        else:
            await self.sio.emit('response', 'ERROR: Invalid game ID', to=sid)
            return False
        
    ### Battle
    
    async def run_battle(self, game_id):
        game = self.games.get(game_id)
        if not game:
            return
        
        frame = 60
        while game_id in self.games.keys() and game.running:
            result = game.step(frame)  # 각 턴 진행
            if result:
                await self.log(game_id, result)
                await self.sio.emit('response', f'{result}', to=self.rooms[game_id])
                await self.sio.emit('round_result', ". ".join(result["message"]), to=self.rooms[game_id])
            await self.send_game_state(game_id)
            await asyncio.sleep(1 / frame)  # 60Frame초 간격으로 턴 진행
        
        await self.declare_winner(game_id)
    
    async def user_score_update(self, user_id, score):
        if user_id in self.user_info.keys():
            self.user_info[user_id]['score'] += score
    
    def save_game_replay(self, game):
        replay = game.get_replay()
        with open(os.path.join(self.replay_path, game.game_id) + ".json", 'w', encoding='utf-8') as file:
            json.dump(replay, file, indent=2, ensure_ascii=False)
    
    async def declare_winner(self, game_id):
        game = self.games.get(game_id)
        if not game:
            return
        self.save_game_replay(game)
        rank_list = game.get_winner()
        for i, user_id in enumerate(rank_list):
            try:
                self.user_info[user_id]['match_results'].append(i+1)
            except:
                pass
            if i < 4:
                score = 4 - i # 4 3 2 1
            else:
                score = 3 - i # -1 -2 -3 -4
            await self.user_score_update(user_id, score)
        
        await self.sio.emit('response', {'game_id': game_id, 'winner': rank_list}, to=self.rooms[game_id])
        await self.log('server', f"Game {game_id} ended. Winner: {rank_list}")
        
        # 게임 종료 후 데이터 정리
        game.stop()
        await self.remove_game(game_id)
        self.save_user_db()
        await self.send_home_state()
    
    # ....
    
    async def send_game_state(self, game_id):
        try:
            for sid in self.rooms[game_id]:
                uid_by_sid = await self.get_user_id(sid) 
                self.user_info[uid_by_sid]['playing'] = True
                await self.send_user_state(sid)
                if uid_by_sid:
                    player = self.games[game_id].get_player_by_user_id(uid_by_sid)
                    if player:
                        await self.sio.emit('update_game', {
                            'game': self.games[game_id].to_json(), 
                            'player': player.to_json()
                        }, to=sid)
        except:
            pass
    
    async def send_lobby_state(self, game_id):
        user_ids = list(self.games[game_id].current_players)
        player_info = [{'user_id': user_id, 'score': self.user_info[user_id]['score']} for user_id in user_ids]
        state = {'game_id': game_id, 'players': player_info}
        await self.sio.emit('update_lobby', state, to=self.rooms[game_id])
    
    async def send_home_state(self):
        game_ids = list(self.games.keys())
        await self.sio.emit('update_home', {'games': [game_id for game_id in game_ids if not self.games[game_id].running]}, to=list(self.clients))
    
    async def send_user_state(self, sid):
        uid_by_sid = await self.get_user_id(sid) 
        if uid_by_sid:
            await self.sio.emit('update_user', self.user_info[uid_by_sid], to=sid)
    
    async def alarm_game_end(self, sid):
        await self.sio.emit('game_end', to=sid)
        
    async def remove_game(self, game_id):
        self.games[game_id].stop()
        await self.sio.emit('update_game', {}, to=self.rooms[game_id])
        await self.sio.emit('quit', to=self.rooms[game_id])
        await self.sio.emit('game_over', to=self.rooms[game_id])
        try:
            self.games.pop(game_id)
            self.rooms.pop(game_id)
        except:
            pass
        await self.send_home_state()
        await self.log('server', f"game {game_id} removed")
    
    async def quit_game(self, sid):
        user_id = await self.get_user_id(sid)
        game_id = await self.get_game_id(sid)

        if user_id and game_id:
            self.user_info[user_id]['game_id'] = None
            self.user_info[user_id]['playing'] = False
            await self.send_user_state(sid)
            await self.alarm_game_end(sid)
            try:
                n_player = self.games[game_id].quit(user_id)
                if n_player == 0:
                    await self.remove_game(game_id)
                else:
                    await self.send_lobby_state(game_id)
            except:
                pass
            await self.log(sid, f'Player {user_id} quit game {game_id}')
            self.save_user_db()

        if user_id:
            self.user_info[user_id]['game_id'] = None
            self.user_info[user_id]['playing'] = False
        await self.sio.emit('quit', to=sid)
        await self.send_user_state(sid)
        return True

    # Player Actions

    async def reroll(self, sid):
        return await self.player_action(sid, 'reroll')
    
    async def buy_exp(self, sid):
        return await self.player_action(sid, 'purchase_exp')
    
    async def buy_unit(self, sid, index):
        return await self.player_action(sid, 'purchase_unit', index)
    
    async def sell_unit(self, sid, source_type, index):
        return await self.player_action(sid, 'sell_unit', source_type, index)
    
    async def move_unit(self, sid, *data):
        return await self.player_action(sid, 'move_unit', data[0], data[1], data[2], data[3])
    
    async def money(self, sid):
        return await self.player_action(sid, 'add_gold', 100)
    
    async def player_action(self, sid, action, *args):
        player = await self.get_player(sid)
        if player and player.active:
            method = getattr(player, action, None)
            if method:
                message = method(*args)
                await self.log(sid, message)
                await self.sio.emit('response', f'{message}', to=sid)
                game_id = await self.get_game_id(sid)
                await self.send_game_state(game_id)
                return message
        return None
    
    # Server Utils
    
    async def get_user_id(self, sid):
        return self.sid_to_user.get(sid)
    
    async def get_game_id(self, sid):
        return self.user_info.get(await self.get_user_id(sid), {}).get('game_id')
    
    async def get_player(self, sid):
        game_id = await self.get_game_id(sid)
        return self.games.get(game_id).get_player_by_user_id(await self.get_user_id(sid)) if game_id in self.games else None

if __name__ == '__main__':
    server = GameServer()
    web.run_app(server.app, host='localhost', port=5000)
    logger.info("Server terminated")

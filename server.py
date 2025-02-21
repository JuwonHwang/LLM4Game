import os
import json
import logging
import socketio
from aiohttp import web
from pyautobattle.src import AutoBattlerGame
import asyncio

# Setup logging
LOG_DIR = 'log'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'server.log')
logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE, format='%(asctime)s, %(name)s, %(levelname)s, %(message)s')
logger = logging.getLogger('game_server')

class GameServer:
    def __init__(self):
        self.user_db_path = 'db/user.json'
        self.load_user_db()
        
        self.sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True, access_log=logger)
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.clients = set()
        self.sid_to_user = {}
        self.user_info = {}
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
        else:
            self.user_info = {}
    
    async def log(self, subject, message):
        logger.info(f"{subject}: {message}")
        print(f"{subject}: {message}")

    async def connect(self, sid, environ):
        self.clients.add(sid)
        await self.log(sid, "Connected")
    
    async def disconnect(self, sid):
        await self.quit_game(sid)
        self.sid_to_user.pop(sid, None)
        self.clients.discard(sid)
        await self.log(sid, "Disconnected")
    
    async def login(self, sid, user_id):
        user_id = user_id[0] if isinstance(user_id, list) else user_id
        self.sid_to_user[sid] = user_id
        
        if user_id not in self.user_info:
            self.user_info[user_id] = {'user_id': user_id, 'score': 100, 'playing': False, 'game_id': None, 'player_id': -1}
            self.save_user_db()
            await self.log(sid, f'User {user_id} created')
        
        await self.log(sid, f'User {user_id} logged in')
        await self.sio.emit('update_home', {"user": self.user_info[user_id], 'games': list(self.games.keys())}, to=sid)
        return True
    
    def save_user_db(self):
        with open(self.user_db_path, 'w', encoding='utf-8') as file:
            json.dump(self.user_info, file, indent=4, ensure_ascii=False)
    
    async def register_game(self, sid, game_id='000'):
        user_id = await self.get_user_id(sid)
        if not user_id:
            await self.sio.emit('response', 'You must log in before registering a game', to=sid)
            return False

        if game_id not in self.games:
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
        self.user_info[user_id]['player_id'] = len(game.current_players)
        if len(game.current_players) > 8:
            await self.sio.emit('response', 'ERROR: Max # of players reached', to=sid)
            return False
        else:
            await self.send_lobby_state(game_id)
            await self.send_home_state()
            return True
    
    async def start_game(self, sid, game_id=None):
        user_id = await self.get_user_id(sid)
        game_id = game_id if user_id == 'ADMIN' else await self.get_game_id(sid)

        if game_id and game_id in self.games:
            self.games[game_id].start()
            asyncio.create_task(self.run_battle(game_id))
            await self.send_game_state(game_id)
            await self.send_home_state()
            await self.log(sid, f"game {game_id} start")
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
            game.step(frame)  # 각 턴 진행
            await self.send_game_state(game_id)
            await asyncio.sleep(1 / frame)  # 60Frame초 간격으로 턴 진행
        
        await self.declare_winner(game_id)
    
    async def declare_winner(self, game_id):
        game = self.games.get(game_id)
        if not game:
            return
        
        winner = game.get_winner()
        await self.sio.emit('game_over', {'game_id': game_id, 'winner': winner}, to=self.rooms[game_id])
        await self.log('server', f"Game {game_id} ended. Winner: {winner}")
        
        # 게임 종료 후 데이터 정리
        game.stop()
        self.games.pop(game_id, None)
        self.rooms.pop(game_id, None)
        await self.send_home_state()
    
    # ....
    
    async def send_game_state(self, game_id):
        for sid in self.rooms[game_id]:
            uid_by_sid = await self.get_user_id(sid) 
            await self.sio.emit('update_game', {
                'game': self.games[game_id].to_json(), 
                'player': self.games[game_id].get_player_by_user_id(uid_by_sid).to_json()
            }, to=sid)
    
    async def send_lobby_state(self, game_id):
        user_ids = list(self.games[game_id].current_players)
        player_info = [{'user_id': user_id, 'score': self.user_info[user_id]['score']} for user_id in user_ids]
        state = {'game_id': game_id, 'players': player_info}
        for sid in self.rooms[game_id]:
            await self.sio.emit('update_lobby', state, to=sid)
    
    async def send_home_state(self):
        game_ids = list(self.games.keys())
        for sid in self.clients:
            await self.sio.emit('update_home', {'games': [game_id for game_id in game_ids if not self.games[game_id].running]}, to=sid)
    
    async def send_user_state(self, sid):
        uid_by_sid = await self.get_user_id(sid) 
        await self.sio.emit('update_user', self.user_info[uid_by_sid])
    
    async def remove_game(self, game_id):
        self.games[game_id].stop()
        for sid in self.rooms[game_id]:
            await self.sio.emit('update_game', {}, to=sid)
            # print(sid)
            await self.sio.emit('quit', to=sid)
        await self.log('server', f"game {game_id} removed")
    
    async def quit_game(self, sid):
        user_id = await self.get_user_id(sid)
        game_id = await self.get_game_id(sid)

        if user_id and game_id:
            self.user_info[user_id]['game_id'] = None
            n_player = self.games[game_id].quit(user_id)
            if n_player == 0:
                await self.remove_game(game_id)
                self.games.pop(game_id)
                self.rooms.pop(game_id)
                await self.send_home_state()
            else:
                self.rooms[game_id].remove(sid)
                await self.sio.emit('quit', to=sid)
            await self.log(sid, f'Player {user_id} quit game {game_id}')
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
                game_id = await self.get_game_id(sid)
                await self.send_game_state(game_id)
                return message
        return False
    
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

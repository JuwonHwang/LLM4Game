import socketio
from aiohttp import web
from pyautobattle.src import AutoBattlerGame, Player
import os
import logging
import json

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
logger = logging.getLogger('game_server')
logger.setLevel(logging.DEBUG)
log_file = os.path.join(log_directory, 'server.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class GameServer:
    def __init__(self):
        self.user_db_file_path = 'db/user.json'
        self.get_user_db()
        self.sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True, access_log=logger)
        self.app = web.Application()
        self.sio.attach(self.app)

        self.clients = set()
        self.sid_to_user = dict()
        self.user_info = dict()
        self.game_dict: dict[str,AutoBattlerGame] = {}

        self.sio.event(self.register_game)
        self.sio.event(self.quit_game)
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.event(self.get_game_state)
        self.sio.event(self.reroll)
        self.sio.event(self.buy_exp)
        self.sio.event(self.buy_unit)
        self.sio.event(self.sell_unit)
        self.sio.event(self.money)
        self.sio.event(self.move_unit)
        self.sio.event(self.login)

    async def log(self, sid, value):
        if isinstance(value, str):
            logger.info(f"{sid}:{value}")
        elif 'message' in value.keys():
            if isinstance(value['message'],list):
                for m in value['message']:
                    logger.info(f"{sid}:{m}")
            else:
                logger.info(f"{sid}:{value['message']}")

    def get_user_db(self):
        with open(self.user_db_file_path, 'r', encoding='utf-8') as file:
            self.user_dict = json.load(file)

    async def connect(self, sid, environ):
        self.clients.add(sid)
        await self.log(sid, "connected")

    async def disconnect(self, sid):
        await self.quit_game(sid)
        if sid in self.sid_to_user:
            self.sid_to_user.pop(sid)
        self.clients.discard(sid)
        await self.log(sid, "disconnected")

    async def login(self, sid, user_id):
        if isinstance(user_id, list):
            user_id = user_id[0]
        self.sid_to_user[sid] = user_id
        if user_id not in self.user_info.keys():
            self.user_info[user_id] = {
                'user_id': user_id,
                'score': 100,
                'playing': False,
                'game_id': -1,
                'player_id': -1,
            }
            with open(self.user_db_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.user_info, file, indent=4, ensure_ascii=False)
            await self.log(sid, f'user {user_id} created')
            await self.sio.emit('response', f'user {user_id} created', to=sid)
        await self.log(sid, f'user {user_id} login')
        await self.sio.emit('response', f'user {user_id} login', to=sid)

    async def register_game(self, sid, game_id='000'):
        user_id = await self.get_user_id_from_sid(sid)
        if user_id is None:
            await self.sio.emit('response', f'You should login before register game', to=sid)
            return
        if game_id not in self.game_dict.keys():
            await self.log(sid, 'make game room')
            game = AutoBattlerGame(game_id)
            self.game_dict[game_id] = game
            self.user_info[user_id]['game_id'] = game_id
            game.register(user_id)
            self.user_info[user_id]['player_id'] = len(game.current_player)
            await self.sio.emit('response', f'You make new game {game_id}', to=sid)
        else:
            await self.log(sid, 'game room exists')
            game = self.game_dict[game_id]
            self.user_info[user_id]['game_id'] = game_id
            game.register(user_id)
            pid = len(game.current_player)
            self.user_info[user_id]['player_id'] = pid
            if pid < 8:
                await self.log(sid, f'player {pid} in game {game_id}')
                await self.sio.emit('response', f'You entered game {game_id}', to=sid)
            else:
                await self.sio.emit('response', 'ERROR: max # of players', to=sid)

    async def get_user_id_from_sid(self, sid):
        if sid not in self.sid_to_user.keys():
            await self.log(sid, f'user for {sid} not exist')
            return None
        return self.sid_to_user[sid]

    async def get_game_id_from_sid(self, sid):
        user_id = await self.get_user_id_from_sid(sid)
        if user_id is None:
            return None
        game_id = self.user_info[user_id]['game_id']
        if game_id not in self.game_dict.keys():
            await self.log(sid, f'game {game_id} not exist')
            return None
        return game_id
    
    async def get_player_from_sid(self, sid):
        user_id = await self.get_user_id_from_sid(sid)
        if user_id is None:
            return None
        game_id = await self.get_game_id_from_sid(sid)
        if game_id is None:
            return None
        return self.game_dict[game_id].get_player_by_user_id(user_id)

    async def quit_game(self, sid):
        user_id = await self.get_user_id_from_sid(sid)
        if user_id is None:
            return
        game_id = await self.get_game_id_from_sid(sid)
        if game_id is None:
            return
        self.user_info[user_id]['game_id'] = -1
        player_id = self.user_info[user_id]['player_id']
        await self.log(sid, f'player {player_id} quit the game')
        num = self.game_dict[game_id].quit(user_id)
        if num == 0:
            await self.log(sid, f'game {game_id} is terminated')

    async def get_game_state(self, sid):
        try:
            user_id = await self.get_user_id_from_sid(sid)
            if user_id is None:
                return
            game_id = await self.get_game_id_from_sid(sid)
            if game_id is None:
                return
            if self.game_dict[game_id].running:
                await self.sio.emit('render', {
                    'game': self.game_dict[game_id].observe(),
                    'player': self.game_dict[game_id].get_player_by_user_id(user_id).observe()
                }, to=sid)
            else:
                await self.sio.emit('lobby', {
                    'game_id': game_id,
                    'players': list(self.game_dict[game_id].current_player)
                })
        except Exception as e:
            await self.log(sid, f"Error in get_game_state: {e}")
            await self.sio.emit('error', {'message': 'An error occurred while fetching game state.'}, to=sid)

    async def reroll(self, sid):
        try:
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                v = player.reroll()
                await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in reroll")
            await self.sio.emit('error', {'api': 'reroll', 'message': e}, to=sid)

    async def buy_exp(self, sid):
        try:
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                v = player.purchase_exp()
                await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in buy_exp")
            await self.sio.emit('error', {'api': 'buy_exp', 'message': e}, to=sid)
            
    async def buy_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                v = player.purchase_unit(index)
                await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in buy_unit")
            await self.sio.emit('error', {'api': 'buy_unit', 'message': e}, to=sid)
            
    async def sell_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                v = player.sell_unit(index)
                await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in sell_unit")
            await self.sio.emit('error', {'api': 'sell_unit', 'message': e}, to=sid)
            
    async def move_unit(self, sid, data=None):
        try:
            if data == None:
                data = []
            if len(data) < 1:
                source_type = 'b'
            else:
                source_type = data[0]
            if len(data) < 2:
                target_type = 'f' if source_type == 'b' else 'b'
            else:
                target_type = data[1]
            if len(data) < 3:
                source_index = 0
            else:
                source_index = int(data[2]) - 1
            if len(data) < 4:
                target_index = 0
            else:
                target_index = int(data[3]) - 1
            if source_type in ["b", "bench"]:
                source_type = "bench"
            elif source_type in ["f", "target"]:
                source_type = "target"
            else:
                raise TypeError("invalid type")
            if target_type in ["b", "bench"]:
                target_type = "bench"
            elif target_type in ["f", "target"]:
                target_type = "target"
            else:
                raise TypeError("invalid type")
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                v = player.move_unit(source_type, target_type, source_index, target_index)
                await self.log(sid, v)
        except Exception as e:
            await self.log(sid, "Error in move_unit")
            # await self.sio.emit('error', {'api': 'move_unit', 'message': e}, to=sid)

    async def money(self, sid):
        try:
            player = await self.get_game_id_from_sid(sid)
            if player is not None:
                player.gold += 100
                await self.log(sid, "gold + 100")
        except Exception as e:
            await self.log(sid, f"Error in money")
            await self.sio.emit('error', {'api': 'money', 'message': e}, to=sid)

if __name__ == '__main__':
    server = GameServer()
    web.run_app(server.app, host='localhost', port=5000)
    logger.info("server terminated")

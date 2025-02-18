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

        self.get_user_db('user.json')
        self.sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True, access_log=logger)
        self.app = web.Application()
        self.sio.attach(self.app)

        self.game: AutoBattlerGame = None
        self.current_user = dict()
        self.player_dict: dict[str, Player] = {}
        self.uid_dict = {}
        self.user_id_dict = dict()

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

    async def log(self, sid, value):
        if isinstance(value, str):
            logger.info(f"{sid}:{value}")
        elif 'message' in value.keys():
            if isinstance(value['message'],list):
                for m in value['message']:
                    logger.info(f"{sid}:{m}")
            else:
                logger.info(f"{sid}:{value['message']}")

    def get_user_db(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            self.user_dict = json.load(file)

    async def connect(self, sid, environ):
        self.connected_users.add(sid)
        await self.log(sid, "connected")

    async def disconnect(self, sid):
        if sid in self.player_dict:
            self.player_dict.pop(sid)
            self.uid_dict.pop(sid)
        if not self.player_dict:
            self.game = None
        self.connected_users.discard(sid)
        await self.log(sid, "disconnected")

    # async def login(self, sid, user_id):
    #     if user_id in self.user_id_dict.keys():
    #         user_id_dict

    async def register_game(self, sid):
        if self.game is None:
            await self.log(sid, 'register game')
            self.game = AutoBattlerGame()
            self.game.start()
        else:
            await self.log(sid, 'game exists')
        uid = len(self.player_dict)
        if uid < 8:
            self.player_dict[sid] = self.game.get_player_by_index(uid)
            self.uid_dict[sid] = uid
            await self.log(sid, f'player {uid}')
        else:
            await self.sio.emit('log', 'ERROR: max # of players', to=sid)

    async def quit_game(self, sid):
        if self.game is not None:
            if sid in self.player_dict:
                self.player_dict.pop(sid)
                uid = self.uid_dict.pop(sid)
                await self.log(sid, f'player {uid} quit the game')
            if not self.player_dict:
                self.game = None
                await self.log(sid, 'the game is terminated')

    async def get_game_state(self, sid):
        try:
            if sid in self.player_dict:
                await self.sio.emit('render', {
                    'game': self.game.observe(),
                    'player': self.player_dict[sid].observe()
                }, to=sid)
        except Exception as e:
            await self.log(sid, f"Error in get_game_state: {e}")
            await self.sio.emit('error', {'message': 'An error occurred while fetching game state.'}, to=sid)

    async def reroll(self, sid):
        try:
            player = self.player_dict[sid]
            v = player.reroll()
            await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in reroll")
            await self.sio.emit('error', {'api': 'reroll', 'message': e}, to=sid)

    async def buy_exp(self, sid):
        try:
            player = self.player_dict[sid]
            v = player.purchase_exp()
            await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in buy_exp")
            await self.sio.emit('error', {'api': 'buy_exp', 'message': e}, to=sid)
            
    async def buy_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = self.player_dict[sid]
            v = player.purchase_unit(index)
            await self.log(sid, v)
        except Exception as e:
            await self.log(sid, f"Error in buy_unit")
            await self.sio.emit('error', {'api': 'buy_unit', 'message': e}, to=sid)
            
    async def sell_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = self.player_dict[sid]
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
            player = self.player_dict[sid]
            v = player.move_unit(source_type, target_type, source_index, target_index)
            await self.log(sid, v)
        except Exception as e:
            await self.log(sid, "Error in move_unit")
            # await self.sio.emit('error', {'api': 'move_unit', 'message': e}, to=sid)

    async def money(self, sid):
        try:
            player = self.player_dict[sid]
            player.gold += 100
            await self.log(sid, "gold + 100")
        except Exception as e:
            await self.log(sid, f"Error in money")
            await self.sio.emit('error', {'api': 'money', 'message': e}, to=sid)

if __name__ == '__main__':
    server = GameServer()
    web.run_app(server.app, host='localhost', port=5000)
    logger.info("server terminated")

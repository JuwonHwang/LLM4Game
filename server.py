import socketio
from aiohttp import web
from pyautobattle.src import AutoBattlerGame, Player

class GameServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='aiohttp', async_handlers=True)
        self.app = web.Application()
        self.sio.attach(self.app)

        self.connected_users = set()
        self.game: AutoBattlerGame = None
        self.player_dict: dict[str, Player] = {}
        self.uid_dict = {}

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

    async def register_game(self, sid):
        if self.game is None:
            print(sid, '- register game')
            self.game = AutoBattlerGame()
            self.game.start()
        else:
            print(sid, '- game exists')
        uid = len(self.player_dict)
        if uid < 8:
            self.player_dict[sid] = self.game.get_player_by_index(uid)
            self.uid_dict[sid] = uid
            print(sid, f'- player {uid}')
        else:
            await self.sio.emit('log', 'ERROR: max # of players', to=sid)

    async def quit_game(self, sid):
        if self.game is not None:
            if sid in self.player_dict:
                self.player_dict.pop(sid)
                uid = self.uid_dict.pop(sid)
                print(sid, f'- player {uid} quit the game')
            if not self.player_dict:
                self.game = None
                print(sid, '- the game is terminated')

    async def connect(self, sid, environ):
        self.connected_users.add(sid)
        print(sid, "- connected")

    async def disconnect(self, sid):
        if sid in self.player_dict:
            self.player_dict.pop(sid)
            self.uid_dict.pop(sid)
        if not self.player_dict:
            self.game = None
        self.connected_users.discard(sid)
        print(sid, "- disconnected")

    async def get_game_state(self, sid):
        try:
            if sid in self.player_dict:
                await self.sio.emit('render', {
                    'game': self.game.observe(),
                    'player': self.player_dict[sid].observe()
                }, to=sid)
        except Exception as e:
            print(f"Error in get_game_state: {e}")
            await self.sio.emit('error', {'message': 'An error occurred while fetching game state.'}, to=sid)

    async def reroll(self, sid):
        try:
            player = self.player_dict[sid]
            player.reroll()
        except Exception as e:
            print(f"Error in reroll")
            await self.sio.emit('error', {'api': 'reroll', 'message': e}, to=sid)

    async def buy_exp(self, sid):
        try:
            player = self.player_dict[sid]
            player.purchase_exp()
        except Exception as e:
            print(f"Error in buy_exp")
            await self.sio.emit('error', {'api': 'buy_exp', 'message': e}, to=sid)
            
    async def buy_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = self.player_dict[sid]
            player.purchase_unit(index)
        except Exception as e:
            print(f"Error in buy_unit")
            await self.sio.emit('error', {'api': 'buy_unit', 'message': e}, to=sid)
            
    async def sell_unit(self, sid, data):
        try:
            index = int(data[0]) - 1
            player = self.player_dict[sid]
            player.sell_unit(index)
        except Exception as e:
            print(f"Error in sell_unit")
            await self.sio.emit('error', {'api': 'sell_unit', 'message': e}, to=sid)
            
    async def money(self, sid):
        try:
            player = self.player_dict[sid]
            player.gold += 100
        except Exception as e:
            print(f"Error in money")
            await self.sio.emit('error', {'api': 'money', 'message': e}, to=sid)

if __name__ == '__main__':
    server = GameServer()
    web.run_app(server.app, host='localhost', port=5000)
    print("server terminated")

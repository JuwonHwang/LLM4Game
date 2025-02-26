import asyncio
import socketio
import json
import os
import random  # 랜덤 액션을 위해 추가
import sys

# Function to load URL from a text file
def load_server_url(filename=".server"):
    try:
        with open(filename, "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("⚠ config.txt not found. Using default URL.")
        return "http://localhost:5000"

SERVER_URL = load_server_url()

class RandomAgentClient:
    def __init__(self, user_id, server_url):
        self.user_id = user_id
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.where = 'home'
        self.update = True
        self.connected = False
        self.state = {"user": {}, "home": {}, "lobby": {}, "game": {}}
        self.register_events()

    def register_events(self):
        @self.sio.event
        async def connect():
            self.connected = True
            print("Connected.")

        @self.sio.event
        async def disconnect():
            self.connected = False
            print("Disconnected.")

        @self.sio.event
        async def response(data):
            print(f"{data}")
            
        @self.sio.event
        async def game_end():
            self.state['game'] = None

        @self.sio.event
        async def update_home(data):
            self.state['home'] = data

        @self.sio.event
        async def update_lobby(data):
            self.state['lobby'] = data

        @self.sio.event
        async def update_game(data):
            self.state['game'] = data
            
        @self.sio.event
        async def update_user(data):
            self.state['user'] = data

    async def connect_to_server(self):
        await self.sio.connect(self.server_url)
        await self.step()
        # await self.sio.wait()

    async def send_command(self, action, params=None):
        if self.sio.connected:
            if params is not None:
                await self.sio.emit(action, params)
            else:
                await self.sio.emit(action)
            return True
        return False

    async def find_game(self):
        games = self.state['home'].get('games')
        if games:
            for game_id in games:
                if self.state['user']['game_id'] is None:
                    await self.send_command('register_game', game_id)
        pass

    async def get_valid_actions(self, money, data):
        actions = ['purchase_exp', 'purchase_unit', 'reroll', 'sell_unit', 'move_unit']
        shop_units = data['shop']['units']
        valid_shop_index = [i for i in range(5) if shop_units[i] is not None and money >= shop_units[i]['cost']]
        valid_sell_pairs = {}
        # TODO
        extra = {
            'purchase_exp': None,
            'reroll': None,
            'purchase_unit': random.randint(0,4),
            'sell_unit': [],
            'move_unit': [random.randint(0,27)],
        }

    async def step(self):
        await self.send_command('login', self.user_id)
        count = 0
        while True:
            await asyncio.sleep(1)  # 1초마다 실행
            if self.state['user'] and self.state['user']['game_id'] is None:
                await self.find_game()
            if self.state['user']['playing']:
                print(count)
                count += 1
            
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    client = RandomAgentClient(user_id, SERVER_URL)

    loop = asyncio.get_event_loop()
    loop.create_task(client.connect_to_server())
    loop.run_forever()
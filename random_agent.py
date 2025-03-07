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
        self.end = False
        self.messages = []
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
            try:
                self.messages.append(json.loads(data))
            except Exception as e:
                pass 
            
        @self.sio.event
        async def game_end():
            self.state['game'] = None

        @self.sio.event
        async def game_over():
            self.end = True

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
            
        async def quit():
            if self.state and self.state['user'] and self.state['user']['playing']:
                self.state['user']['playing'] = False

    async def connect_to_server(self):
        await self.sio.connect(self.server_url)
        await self.step()
        # await self.sio.wait()
        return

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
        else:
            await self.send_command('register_game')
        pass

    def get_valid_actions(self, money, data):
        actions = ['buy_exp', 'buy_unit', 'reroll', 'sell_unit', 'move_unit', 'none']

        shop_units = data['player']['shop']['units']
        bench_units = data['player']['bench']['units']
        field_units = data['player']['field']['units']
        
        shop_num_slots = data['player']['shop']['num_slots']
        bench_num_slots = data['player']['bench']['num_slots']
        field_num_slots = data['player']['field']['num_slots']
        
        valid_shop_index = [i for i in range(shop_num_slots) if shop_units[i] is not None and money >= shop_units[i]['cost']]
        
        valid_bench_positions = []
        for bench_index, bench_unit in enumerate(bench_units):
            if bench_unit is not None:
                valid_bench_positions.append(bench_index)
        
        valid_field_positions = []
        for field_index, field_unit in enumerate(field_units):
            if field_unit is not None:
                valid_field_positions.append(field_index)
                
        valid_source_positions = []
        for bench_pos in valid_bench_positions:
            valid_source_positions.append(('bench', bench_pos))
        for field_pos in valid_field_positions:
            valid_source_positions.append(('field', field_pos))
        
        valid_target_positions = []
        for i in range(bench_num_slots):
            valid_target_positions.append(('bench', i))
        for i in range(field_num_slots):
            valid_target_positions.append(('field', i))
        
        # TODO
        extra = {
            'buy_exp': [None,],
            'reroll': [None,],
            'buy_unit': valid_shop_index,
            'sell_unit': valid_source_positions,
            'move_unit': [valid_source_positions, valid_target_positions],
        }
        
        if money < 4:
            actions.remove('buy_exp')
            extra.pop('buy_exp')
        if money < 2:
            actions.remove('reroll')
            extra.pop('reroll')
        if len(valid_shop_index) == 0:
            actions.remove('buy_unit')
            extra.pop('buy_unit')
        if len(valid_source_positions) == 0:
            actions.remove('sell_unit')
            extra.pop('sell_unit')
            actions.remove('move_unit')
            extra.pop('move_unit')
        return actions, extra
    
    async def get_action(self, actions, extra):
        action = random.choice(actions)
        if action == 'none':
            return None, None
        elif action == 'move_unit':
            source = random.choice(extra[action][0])
            target = random.choice(extra[action][1])
            return action, (source[0], target[0], source[1], target[1])
        else:
            arg = random.choice(extra[action])
            return action, arg        
        
    async def step(self):
        await self.send_command('login', self.user_id)
        count = 0
        while not self.end:
            if self.state['user'] and self.state['user']['game_id'] is None:
                await self.find_game()
            elif self.state['user'] and self.state['user']['game_id'] is not None:
                break
            await asyncio.sleep(0.1)
        while not self.end:
            if self.state and self.state['user'] and self.state['user']['playing']:
                actions, extra = self.get_valid_actions(self.state['game']['player']['gold'], self.state['game'])
                if self.state["game"]["player"]["active"] and self.state['game']['player']['hp'] > 0:
                    action, arg = await self.get_action(actions, extra)
                    if action is not None:
                        await self.send_command(action, arg)
                    count += 1
            await asyncio.sleep(1)  # 1초마다 실행
        await self.send_command("quit_game", None)
        await self.close()
        return
    
    async def close(self):
        if self.sio.connected:
            await self.sio.disconnect()  # Properly close the socket connection
            print(f"{self.user_id} disconnected.")
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    client = RandomAgentClient(user_id, SERVER_URL)

    loop = asyncio.get_event_loop()
    loop.create_task(client.connect_to_server())
    loop.run_until_complete()
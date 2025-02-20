import asyncio
import socketio
import json
import os

from ui.render import render_lobby, render_home, render_game

class GameClient:
    def __init__(self, server_url):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.keymap = {
            'd': 'reroll',
            'e': 'sell_unit',
            'w': 'move_unit',
            'f': 'buy_exp',
            'g': 'buy_unit',
        }
        self.current_state = None
        self.playing = False
        self.where = 'home'
        self.update = True
        self.state = {
            'home': {
                'user': {
                    'user_id': None,
                    'score': None
                },
                'games': []
            },
        }
        self.game_list = []
        self.register_events()

    def register_events(self):
        @self.sio.event
        async def connect():
            print("Connected.")
            request_task = asyncio.create_task(self.render())
            await self.send_commands()

        @self.sio.event
        async def disconnect():
            print("Disconnected.")

        @self.sio.event
        async def response(data):
            print(f"{data}")
                    
        @self.sio.event
        async def update_home(data):
            self.state['home'] = data
            if self.where == 'home':
                self.update = True
                
        @self.sio.event
        async def update_lobby(data):
            self.state['lobby'] = data
            self.update = True

        @self.sio.event
        async def update_game(data):
            self.state['game'] = data
            self.update = True
            
        @self.sio.event
        async def quit():
            try:
                self.state.pop('game')
            except Exception as e:
                print(e)
            try:
                self.state.pop('lobby')
            except Exception as e:
                print(e)

    async def connect_to_server(self):
        await self.sio.connect(self.server_url)
        await self.sio.wait()

    async def render(self):
        while True:
            await self.sio.sleep(1/30)
            if self.update:
                self.update = False
                self.clear_terminal()
                try:
                    print(self.state.keys())
                    if 'game' in self.state.keys():
                        render_game(self.state)
                    elif 'lobby' in self.state.keys():
                        render_lobby(self.state)
                    else:
                        render_home(self.state)
                except Exception as e:
                    print(e)
            
    async def send_commands(self):
        while True:
            command = await asyncio.get_event_loop().run_in_executor(None, input, "")
            command = command.lower()
            command = command.split()
            if len(command) == 0:
                pass
            elif command[0] == 'exit':
                await self.sio.disconnect()
                break
            elif command[0] == 'register':
                if len(command) == 1:
                    await self.sio.emit('register_game', '0')
                else:
                    await self.sio.emit('register_game', command[1])
            elif command[0] == 'start':
                if len(command) == 1:
                    await self.sio.emit('start_game', command[0])
                else:
                    await self.sio.emit('start_game', command[0], command[1])
            elif command[0] == 'quit':
                await self.sio.emit('quit_game')
            else:
                try:
                    action = command[0]
                    if action in self.keymap.keys():
                        action = self.keymap[action]
                    if len(command) > 1:
                        await self.sio.emit(action, command[1:])
                    else:
                        await self.sio.emit(action)
                except Exception as e:
                    print("Invalid command...")
            self.update = True

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')
        
if __name__ == '__main__':
    client = GameClient('http://localhost:5000')
    asyncio.run(client.connect_to_server())
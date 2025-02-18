import asyncio
import socketio
import json
import os
from pyautobattle.src.render import client_render

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
        self.register_events()

    def register_events(self):
        @self.sio.event
        async def connect():
            print("Connected.")
            request_task = asyncio.create_task(self.request_game_state())
            await self.send_commands()

        @self.sio.event
        async def disconnect():
            print("Disconnected.")

        @self.sio.event
        async def response(data):
            print(f"{data}")

        @self.sio.event
        async def render(data):
            if self.current_state == data:
                pass
            else:
                self.current_state = data
                self.clear_terminal()
                try:
                    client_render(data['game'], data['player'])
                except Exception as e:
                    print(e)
            
        @self.sio.event
        async def lobby(data):
            if self.current_state == data:
                pass
            else:
                self.current_state = data
                self.clear_terminal()
                try:
                    print('Game ID:', data['game_id'])
                    players = data['players']
                    print("--LOBBY--")
                    for player in players:
                        print(player)
                    print("---------")
                except Exception as e:
                    print(e)

    async def request_game_state(self):
        while True:
            await self.sio.sleep(1/30)
            if self.sio.connected and self.playing:
                try:
                    await self.sio.emit('get_game_state')
                except Exception as e:
                    print(e)

    async def connect_to_server(self):
        await self.sio.connect(self.server_url)
        await self.sio.wait()

    async def send_commands(self):
        while True:
            command = await asyncio.get_event_loop().run_in_executor(None, input, ">>> ")
            command = command.lower()
            command = command.split()
            if len(command) == 0:
                pass
            elif command[0] == 'exit':
                await self.sio.disconnect()
                break
            elif command[0] == 'register':
                await self.sio.emit('register_game', command[1])
                self.playing = True
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

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')
        
if __name__ == '__main__':
    client = GameClient('http://localhost:5000')
    asyncio.run(client.connect_to_server())
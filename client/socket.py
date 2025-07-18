import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import QThread, pyqtSignal

class SocketThread(QThread):
    update_ui = pyqtSignal(dict)
    
    def __init__(self, parent, loop, server_url):
        super().__init__()
        self.parent = parent
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.state = {"user": {}, "home": {}, "lobby": {}, "game": {}}
        self.update = False
        self.loop = loop  # 기존 이벤트 루프를 가져옴
        self.register_events()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def connect_to_server(self):
        while True:
            try:
                await self.sio.connect(self.server_url)
                await self.sio.wait()
                break
            except (socketio.exceptions.ConnectionError, asyncio.TimeoutError) as e:
                await asyncio.sleep(1)

    async def send_command(self, action, params=None):
        if self.sio.connected:
            if params is not None:
                await self.sio.emit(action, params)
            else:
                await self.sio.emit(action)
            return True
        return False
            
    def register_events(self):
        @self.sio.event
        async def connect():
            print("Connected.")

        @self.sio.event
        async def disconnect():
            print("Disconnected.")

        @self.sio.event
        async def response(data):
            print(f"{data}")
            
        @self.sio.event
        async def game_end():
            self.state.pop('game')
            if self.parent is not None:
                self.parent.stacked_widget.setCurrentWidget(self.parent.home_screen)

        @self.sio.event
        async def update_home(data):
            self.state['home'] = data
            self.update_ui.emit(self.state)

        @self.sio.event
        async def update_lobby(data):
            self.state['lobby'] = data
            self.update_ui.emit(self.state)

        @self.sio.event
        async def update_game(data):
            self.state['game'] = data
            self.update_ui.emit(self.state)
            
        @self.sio.event
        async def update_user(data):
            self.state['user'] = data
            self.update_ui.emit(self.state)
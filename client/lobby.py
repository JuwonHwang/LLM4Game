import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import QThread, pyqtSignal
from .baseWidget import BaseWidget

class LobbyScreen(BaseWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        
        self.game_id_label = QLabel()
        self.user_list = QListWidget()
        
        self.btn_start = QPushButton("▶ Start Game")
        self.btn_start.clicked.connect(self.start_game)
        
        layout.addWidget(self.game_id_label)
        layout.addWidget(QLabel("👤 Users"))
        layout.addWidget(self.user_list)
        layout.addWidget(self.btn_start)
        
        self.setLayout(layout)
    
    def start_game(self):
        self.parent.run_async(self.parent.socket_thread.send_command("start_game"))
        self.parent.stacked_widget.setCurrentWidget(self.parent.game_screen)
        
    def update_state(self, data):
        if 'game_id' in data.keys():
            self.game_id_label.setText(f"🕹️ Game Room ID - {data['game_id']}")
        if 'players' in data.keys():
            self.update_user_list(data['players'])
        
    def update_user_list(self, users):
        self.user_list.clear()
        for user in users:
            # print(user)
            self.user_list.addItem(user)
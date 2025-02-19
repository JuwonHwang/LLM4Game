import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime
from .baseWidget import BaseWidget

class HomeScreen(BaseWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        
        self.game_list = QListWidget()
        self.game_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.btn_register = QPushButton("🆕 Register Game")
        self.btn_register.clicked.connect(self.register_game)
        
        layout.addWidget(QLabel("🎮 Available Games:"))
        layout.addWidget(self.game_list)
        layout.addWidget(self.btn_register)
        
        self.setLayout(layout)
    
    def register_game(self):
        if len(self.game_list.selectedItems()) > 0:
            game_id = self.game_list.selectedItems()[0].text()
        else:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S_")
            game_id = current_time + str(len(self.game_list))
        self.parent.run_async(self.parent.socket_thread.send_command("register_game", game_id))
        self.parent.stacked_widget.setCurrentWidget(self.parent.lobby_screen)
    
    def update_state(self, data):
        if 'games' in data.keys():
            self.update_game_list(data['games'])
    
    def update_game_list(self, games):
        self.game_list.clear()
        for game in games:
            # print(game)
            self.game_list.addItem(game)
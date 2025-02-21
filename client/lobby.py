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
        control_layout = QHBoxLayout()
        
        self.game_id_label = QLabel()
        self.user_list = QListWidget()
        
        self.btn_start = QPushButton("▶ Start Game")
        self.btn_start.clicked.connect(self.start_game)
        self.btn_quit = QPushButton("❌ Quit Game")
        self.btn_quit.setStyleSheet(f"""
            QPushButton {{
                    background-color: rgb(200, 80, 80);
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgb(220, 120, 120);
                }}
            """)
        self.btn_quit.clicked.connect(self.quit)
        
        layout.addWidget(self.game_id_label)
        layout.addWidget(QLabel("👤 Users"))
        layout.addWidget(self.user_list)
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_quit)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
    
    def start_game(self):
        v = self.parent.run_async(self.parent.socket_thread.send_command("start_game"))
        if v:
            self.parent.stacked_widget.setCurrentWidget(self.parent.game_screen)
        
    def update_state(self, data):
        if 'game_id' in data.keys():
            self.game_id_label.setText(f"🕹️ Game Room ID - {data['game_id']}")
        if 'players' in data.keys():
            self.update_user_list(data['players'])
        
    def update_user_list(self, users):
        self.user_list.clear()
        for user in users:
            user_id = user['user_id']
            score = user['score']
            self.user_list.addItem(f"{user_id} (score: {score})")

    def quit(self):
        v = self.parent.run_async(self.parent.socket_thread.send_command("quit_game", None))
        self.parent.socket_thread.state["game"] = {}
        if v:
            self.parent.stacked_widget.setCurrentWidget(self.parent.home_screen)
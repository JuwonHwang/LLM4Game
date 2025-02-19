import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget, QGridLayout
)
from PyQt6.QtCore import QThread, pyqtSignal

from .game_ui.shop_widget import ShopWidget
from .game_ui.bench_widget import BenchWidget
from .game_ui.field_widget import FieldWidget

from .baseWidget import BaseWidget

class GameScreen(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/styles.qss")
        self.parent = parent
        layout = QVBoxLayout()
        self.player_info_layout = QHBoxLayout()
        self.player_buttons = []
        layout.addLayout(self.player_info_layout)
        
        control_layout = QHBoxLayout()
        
        self.shop_layout = ShopWidget(self)
        self.bench_layout = BenchWidget(self)
        self.field_layout = FieldWidget(self)
        
        self.btn_exp = QPushButton("🆙 Buy EXP")
        self.btn_reroll = QPushButton("🔄️ Reroll")
        self.btn_quit = QPushButton("❌ Quit Game")
        
        self.btn_exp.clicked.connect(lambda: self.send_command("buy_exp"))
        self.btn_reroll.clicked.connect(lambda: self.send_command("reroll"))
        self.btn_quit.clicked.connect(self.quit)
        
        control_layout.addWidget(self.btn_exp)
        control_layout.addWidget(self.btn_reroll)
        control_layout.addWidget(self.btn_quit)
        layout.addWidget(self.field_layout)
        layout.addWidget(self.bench_layout)
        layout.addWidget(self.shop_layout)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
        
    def update_state(self, data: dict):
        if len(data.keys()) == 0:
            return
        player = data['player']
        # self.raw_data.setText(json.dumps(player, indent=4))
        self.shop_layout.update_state(player['shop'])
        self.bench_layout.update_state(player['bench'])
        self.field_layout.update_state(player['field'])
        
    def send_command(self, action, *args):    
        self.parent.run_async(self.parent.socket_thread.send_command(action, args))
    
    def select_bench(self, index):
        self.bench_index = index
        
    def select_field(self, index):
        self.field_index = index
    
    def quit(self):
        self.send_command("quit_game")
        self.parent.stacked_widget.setCurrentWidget(self.parent.home_screen)
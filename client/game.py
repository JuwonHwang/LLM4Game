import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget, QGridLayout
)
from PyQt6.QtGui import QPalette, QBrush, QColor

from .game_ui.shop_widget import ShopWidget
from .game_ui.bench_widget import BenchWidget
from .game_ui.field_widget import FieldWidget
from .game_ui.player_widget import PlayerWidget
from .game_ui.unit_widget import UnitWidget
from .game_ui.game_state_widget import GameStateWidget

from .baseWidget import BaseWidget

class GameScreen(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/styles.qss")
        self.parent = parent
        self.state = None
        
        self.basic_styles = "client/game_ui/game_styles.qss"
        
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        center_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        
        control_layout = QVBoxLayout()
        self.btn_exp = QPushButton("🆙 Buy EXP (4🪙)")
        self.btn_exp.setStyleSheet(f"""
            QPushButton {{
                    background-color: rgb(80, 140, 200);
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgb(126, 185, 200);
                }}
            """)
        self.btn_reroll = QPushButton("🔄️ Reroll (2🪙)")
        self.btn_reroll.setStyleSheet(f"""
            QPushButton {{
                    background-color: rgb(200, 160, 80);
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgb(220, 185, 120);
                }}
            """)
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
        
        self.game_state_widget = GameStateWidget(self)
        self.synergy_widget = QLabel("Synergy")
        self.item_widget = QLabel("Item")
        
        self.map_widget = QLabel("Map")
        self.unit_widget = UnitWidget(self)
        
        self.shop_layout = ShopWidget(self)
        self.bench_layout = BenchWidget(self)
        self.field_layout = FieldWidget(self)
        self.player_layout = PlayerWidget(self)
        
        self.player_info_layout = QVBoxLayout()
        self.player_buttons = []
        
        self.btn_exp.clicked.connect(lambda: self.send_command("buy_exp"))
        self.btn_reroll.clicked.connect(lambda: self.send_command("reroll"))
        self.btn_quit.clicked.connect(self.quit)
        
        control_layout.addWidget(self.btn_exp)
        control_layout.addWidget(self.btn_reroll)
        right_layout.addWidget(self.btn_quit)
        
        bottom_layout.addLayout(control_layout)
        bottom_layout.addWidget(self.shop_layout)
        
        center_layout.addWidget(self.game_state_widget)
        center_layout.addWidget(self.field_layout)
        center_layout.addWidget(self.bench_layout)
        center_layout.addWidget(self.player_layout)
        center_layout.addLayout(bottom_layout)
        
        left_layout.addWidget(self.synergy_widget)
        left_layout.addWidget(self.item_widget)
        
        right_layout.addWidget(self.map_widget)
        right_layout.addWidget(self.unit_widget)
        
        layout.addLayout(left_layout)
        layout.addLayout(center_layout)
        layout.addLayout(right_layout)
        
        self.setLayout(layout)
        self.refresh_style()
        self.setAcceptDrops(True)  # Accept drops
        
    def dragEnterEvent(self, a0):
        self.refresh_style()
        return super().dragEnterEvent(a0)
    
    def dragLeaveEvent(self, a0):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#AAAAFA"))
        for w in [self.bench_layout, self.field_layout, self.shop_layout]:
            w.setAutoFillBackground(True)
            w.setPalette(palette)
        
        return super().dragLeaveEvent(a0)
    
    def refresh_style(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#AAAAAA"))
        for w in [self.bench_layout, self.field_layout, self.shop_layout]:
            w.setAutoFillBackground(True)
            w.setPalette(palette)
        
    def update_state(self, data: dict):
        if len(data.keys()) == 0:
            return
        game = data['game']
        player = data['player']
        if not self.state or self.state['player']['shop'] != player['shop']:
            self.shop_layout.update_state(player['shop'])
        if not self.state or self.state['player']['bench'] != player['bench']:
            self.bench_layout.update_state(player['bench'])
        if not self.state or self.state['player']['field'] != player['field']:
            self.field_layout.update_state(player['field'])
        if not self.state or self.state['game']['state'] != game['state']:
            self.game_state_widget.update_state(game["state"])
            self.field_layout.set_game_state(game["state"]["current_state"])
        if not self.state or self.state['player'] != player:
            self.player_layout.update_state(player)
        self.state = data
        self.refresh_style()
        
    def view_unit(self, where, index):
        if self.state['player']:
            self.unit_widget.update_state(self.state['player'][where]['units'][index])
        
    def send_command(self, action, *args):    
        return self.parent.run_async(self.parent.socket_thread.send_command(action, args))
    
    def select_bench(self, index):
        self.bench_index = index
        
    def select_field(self, index):
        self.field_index = index
    
    def quit(self):
        self.send_command("quit_game")
        self.parent.socket_thread.state["game"] = {}
        self.parent.stacked_widget.setCurrentWidget(self.parent.home_screen)
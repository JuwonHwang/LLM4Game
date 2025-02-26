from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json
from PyQt6.QtGui import QPalette, QBrush, QColor

class PlayerWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/player_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        # 배경색 설정
        # palette = QPalette()
        # palette.setColor(QPalette.ColorRole.Window, QColor("#200000"))
        # self.setAutoFillBackground(True)
        # self.setPalette(palette)

        self.info_layout = QHBoxLayout()
        # self.gold_layout = QHBoxLayout()
        self.unit_rate_layout = QHBoxLayout()
        self.unit_rate_label_list = []
        for i in range(5):
            label = QLabel()
            self.unit_rate_label_list.append(label)
            self.unit_rate_layout.addWidget(label)
            color = self.color_map[i+1]
            self.unit_rate_label_list[i].setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 8px;
                }}
            """)
        
        self.level_label = QLabel()
        self.exp_label = QLabel()
        self.hp_label = QLabel()
        self.id_label = QLabel()
        self.gold_label = QLabel()
        self.streak_label = QLabel()
        
        self.info_layout.addWidget(self.id_label)
        self.info_layout.addWidget(self.hp_label)
        self.info_layout.addWidget(self.level_label)
        self.info_layout.addWidget(self.exp_label)
        self.info_layout.addWidget(self.gold_label)
        self.info_layout.addWidget(self.streak_label)
        
        main_layout.addLayout(self.info_layout)
        # main_layout.addLayout(self.gold_layout)
        main_layout.addLayout(self.unit_rate_layout)
        self.setLayout(main_layout)

    def update_state(self, data):
        # print(data)
        self.id_label.setText(f"ID: {data['id']}")
        self.hp_label.setText(f"HP: {data['hp']}")
        self.level_label.setText(f"LEVEL: {data['level']}")
        self.exp_label.setText(f"EXP: {data['exp']} / {data['req_exp']}")
        self.gold_label.setText(f"GOLD: 🪙{data['gold']}")
        streak_emoji = '🔥' if data['streak'] >= 0 else '💦'
        streak_value = abs(data['streak'])
        self.streak_label.setText(f"{streak_emoji} {streak_value}")
        for i in range(5):
            rate = int(data['unit_rate'][i] * 100)
            self.unit_rate_label_list[i].setText(f"{i+1}🪙 {rate}%")
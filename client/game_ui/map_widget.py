from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json
from PyQt6.QtGui import QPalette, QBrush, QColor

class MapWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/player_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        
        self.players_layout = QVBoxLayout()
        self.buttons = []
        for index in range(8):
            button = QPushButton(f"Player {index}")
            button.clicked.connect(lambda _, i=index: self.parent.set_view_player(i))
            self.buttons.append(button)
            self.players_layout.addWidget(button)
            
        main_layout.addLayout(self.players_layout)
        self.setLayout(main_layout)

    def update_state(self, data):
        if data:
            for i in range(8):
                pid = data[i]['id']
                hp = data[i]['hp']
                self.buttons[i].setText(f"{pid} ({hp})")
                if hp <= 0:
                    self.buttons[i].setDisabled(True)
                else:
                    self.buttons[i].setDisabled(False)
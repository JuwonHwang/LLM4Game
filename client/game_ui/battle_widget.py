from PyQt6.QtWidgets import QLineEdit, QGridLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import QSize
from .drag_widget import DraggableLabel

from ..game_ui.util import unit_to_text, get_color
from ..baseWidget import BaseWidget
from .battle_unit_widget import BattleUnitWidget
import json

class BattleWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        
        self.raw_data = QLineEdit()
        self.unit_layout = QGridLayout()
        self.unit_buttons = [] 
        
        # main_layout.addWidget(self.raw_data)
        main_layout.addLayout(self.unit_layout)

        self.setLayout(main_layout)

    def clear_button_layout(self):
        """Clear all widgets from self.button_layout"""
        self.unit_buttons.clear()
        while self.unit_layout.count():
            item = self.unit_layout.takeAt(0)  # Take the first item
            widget = item.widget()  # Get the widget
            if widget:
                widget.deleteLater()  # Properly delete the widget

    def update_state(self, data):
        self.clear_button_layout()
        self.raw_data.setText(f'{data}')
        if not data:
            return
        team = data['team']
        arena = data['arena']
        button = QPushButton()
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #cccccc;
                color: white;
            }}
        """)
        units = [[None for j in range(7)] for i in range(8)]
        
        for unit_info in arena:
            unit = unit_info['unit']
            pos = unit_info['pos']
            name = unit_to_text(unit)
            if team == 'home':
                units[7-pos[0]][pos[1]] = unit
            else:
                units[pos[0]][6-pos[1]] = unit

        for row in range(8):
            for col in range(7):
                unit = units[row][col]
                color, hover_color = get_color(unit)
                button = BattleUnitWidget(unit, color, hover_color)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.unit_layout.addWidget(button, row, col)
                self.unit_buttons.append(button) 
                
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json

class FieldWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QVBoxLayout()
        label = QLabel("Field")
        main_layout.addWidget(label)

        self.button_layout = QHBoxLayout()
        self.buttons = [] 
        
        main_layout.addLayout(self.button_layout)
        self.setAcceptDrops(True)  # Accept drops
        self.setLayout(main_layout)

    def clear_button_layout(self):
        """Clear all widgets from self.button_layout"""
        self.buttons.clear()
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)  # Take the first item
            widget = item.widget()  # Get the widget
            if widget:
                widget.deleteLater()  # Properly delete the widget

    def dropped(self, data):
        if data is None:
            pass
        else:
            if data['source'] == "shop":
                self.parent.send_command('buy_unit', data['index'])
            else:
                self.parent.send_command('move_unit', data['source'], 'field', data['index'], data['target_index'])

    def update_state(self, data):
        self.clear_button_layout()
        unit_list = data['units']
        for index, unit in enumerate(unit_list):
            name = unit_to_text(unit)
            btn = DraggableLabel(name, 'field', index)
            self.button_layout.addWidget(btn)
            self.buttons.append(btn) 
            
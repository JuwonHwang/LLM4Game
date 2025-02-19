from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json

class BenchWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QVBoxLayout()
        label = QLabel("Bench")
        main_layout.addWidget(label)

        self.button_layout = QHBoxLayout()
        self.buttons = [] 
        
        button_names = [None for _ in range(9)]
        for index, name in enumerate(button_names):
            btn = DraggableLabel(name, 'bench', index)
            # btn.clicked.connect(lambda _, i=index: self.select(i))
            self.button_layout.addWidget(btn)
            self.buttons.append(btn) 

        main_layout.addLayout(self.button_layout)
        self.setLayout(main_layout)

        # self.setAcceptDrops(True)  # Accept drops

    def dropped(self, data):
        if data is None:
            pass
        else:
            if data['source'] == "shop":
                self.parent.send_command('buy_unit', data['index'])
            else:
                self.parent.send_command('move_unit', data['source'], 'bench', data['index'], data['target_index'])
                
    def update_state(self, data):
        unit_list = data['units']
        for index, button in enumerate(self.buttons):
            unit = unit_list[index]
            button.setText(unit_to_text(unit))
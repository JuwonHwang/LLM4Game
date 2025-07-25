from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QSizePolicy
from ..game_ui.util import unit_to_text, get_color
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json

class BenchWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        # label = QLabel("Bench")
        # main_layout.addWidget(label)

        self.button_layout = QHBoxLayout()
        self.buttons = [] 
        
        button_names = [None for _ in range(9)]
        for index, name in enumerate(button_names):
            button = DraggableLabel(self, name, 'bench', index)
            button.clicked.connect(lambda _, i=index: self.parent.view_unit('bench', i))
            self.button_layout.addWidget(button)
            self.buttons.append(button) 
            

        main_layout.addLayout(self.button_layout)
        self.setLayout(main_layout)

        self.setAcceptDrops(True)  # Accept drops

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropped(self, data):
        if data is None:
            pass
        else:
            if data['source'] == "shop":
                self.parent.send_command('buy_unit', data['index'])
            else:
                self.parent.send_command('move_unit', data['source'], 'bench', data['index'], data['target_index'])
                
    def dropEvent(self, event):
        data = event.mimeData().data("application/json").data().decode("utf-8")
        data = json.loads(data)
        if data['source'] == "shop":
            self.parent.send_command('buy_unit', data['index'])
        else:
            self.parent.send_command('move_unit', data['source'], 'bench', data['index'], -1)
        self.parent.refresh_style()
        event.acceptProposedAction()
                
    def update_state(self, data):
        unit_list = data['units']
        for index, button in enumerate(self.buttons):
            unit = unit_list[index]
            button.setText(unit_to_text(unit))
            color, hover_color = get_color(unit)
            if unit is not None:
                button.dragable = True
            else:
                button.dragable = False
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from ..game_ui.util import unit_to_shop_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json

class ShopWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        label = QLabel("Shop")
        
        main_layout.addWidget(label)

        self.button_layout = QHBoxLayout()
        self.buttons = [] 
        
        button_names = ["button 1", "button 2", "button 3", "button 4", "button 5"]
        for index, name in enumerate(button_names):
            btn = DraggableLabel(name, 'shop', index)
            btn.clicked.connect(lambda _, i=index: self.parent.view_unit('shop', i))
            self.button_layout.addWidget(btn)
            self.buttons.append(btn)

        main_layout.addLayout(self.button_layout)
        self.setAcceptDrops(True)  # Accept drops
        self.setLayout(main_layout)

    def dropped(self, data):
        if data is None:
            pass
        else:
            if data['source'] == "field":
                pass
            if data['source'] == "bench":
                self.parent.send_command('sell_unit', data['index'])
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
                
    def dropEvent(self, event):
        data = event.mimeData().data("application/json").data().decode("utf-8")
        data = json.loads(data)
        if data['source'] == "bench":
            self.parent.send_command('sell_unit', data['index'])
        self.parent.refresh_style()
        event.acceptProposedAction()
                
    def update_state(self, data):
        unit_list = data['units']
        for index, button in enumerate(self.buttons):
            unit = unit_list[index]
            if unit is not None:
                color = self.color_map[unit['cost']]
                hover_color = self.hover_color_map[unit['cost']]
                button.dragable = True
            else:
                color = "#eeeeee"
                hover_color = "#eeeeee"
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
            button.setText(unit_to_shop_text(unit))
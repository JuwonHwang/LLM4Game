from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_shop_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel

class ShopWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QVBoxLayout()
        label = QLabel("Shop")
        main_layout.addWidget(label)

        self.button_layout = QHBoxLayout()
        self.buttons = [] 

        self.color_map = [
            "#000000",
            "#95a5a6",  # Gray
            "#1abc9c",  # Turquoise
            "#3498db",  # Blue
            "#9b59b6",  # Purple
            "#f1c40f"   # Yellow
        ]
        self.hover_color_map = [
            "#333333",  # Black → Dark Gray
            "#bdc3c7",  # Gray → Lighter Gray
            "#48e0c2",  # Turquoise → Lighter Turquoise
            "#5dade2",  # Blue → Lighter Blue
            "#af7ac5",  # Purple → Lighter Purple
            "#f4d03f"   # Yellow → Lighter Yellow
        ]
        
        button_names = ["button 1", "button 2", "button 3", "button 4", "button 5"]
        for index, name in enumerate(button_names):
            btn = DraggableLabel(name, 'shop', index)
            # btn.clicked.connect(lambda _, i=index: self.parent.send_command('buy_unit', i))
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
                
    def update_state(self, data):
        unit_list = data['units']
        for index, button in enumerate(self.buttons):
            unit = unit_list[index]
            if unit is not None:
                color = self.color_map[unit['cost']]
                hover_color = self.hover_color_map[unit['cost']]
                button.setStyleSheet(f"""
                    QWidget {{
                        background-color: {color};
                        color: white;
                        font-size: 16px;
                        padding: 10px;
                        border-radius: 8px;
                    }}
                    QWidget:hover {{
                        background-color: {hover_color};
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QWidget {{
                        background-color: #eeeeee;
                        color: white;
                        font-size: 16px;
                        padding: 10px;
                        border-radius: 8px;
                    }}
                    QWidget:hover {{
                        background-color: #eeeeee;
                    }}
                """)
            button.setText(unit_to_shop_text(unit))
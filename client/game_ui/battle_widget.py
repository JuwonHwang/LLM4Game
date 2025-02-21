from PyQt6.QtWidgets import QApplication, QStackedWidget, QGridLayout, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
import json

class BattleWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()

        self.unit_layout = QGridLayout()
        self.unit_buttons = [] 
        
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
        # enemy = data['enemy']
        # ally = data['ally']
        # unit_list = data['units']
        # max_units = data['max_units']
        # unit_count = len([unit for unit in unit_list if unit is not None])
        # self.left_label.setText(f"Field\n( {unit_count} / {max_units} )")
        # for index in range(len(unit_list)):
        #     button = QPushButton()
        #     button.setStyleSheet(f"""
        #         QPushButton {{
        #             background-color: #cccccc;
        #             color: white;
        #         }}
        #     """)
        #     self.unit_layout.addWidget(button, index // 7, index % 7)

        # for index, unit in enumerate(unit_list):
        #     name = unit_to_text(unit)
        #     button = QPushButton(name)
        #     button.clicked.connect(lambda _, i=index: self.parent.view_unit('battle', i))
        #     self.unit_layout.addWidget(button, index // 7 + 4, index % 7)
        #     self.unit_buttons.append(button) 
        #     if unit is not None:
        #         color = self.color_map[unit['cost']]
        #         hover_color = self.hover_color_map[unit['cost']]
        #     else:
        #         color = "#eeeeee"
        #         hover_color = "#eeeeee"
        #     button.setStyleSheet(f"""
        #         QPushButton {{
        #             background-color: {color};
        #             color: white;
        #         }}
        #         QPushButton:hover {{
        #             background-color: {hover_color};
        #         }}
        #     """)
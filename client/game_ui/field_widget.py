from PyQt6.QtWidgets import QApplication, QStackedWidget, QGridLayout, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel

from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget
from .drag_widget import DraggableLabel
import json

class FieldWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()
        self.left_label = QLabel("Field\n( 0 / 0 )")
        self.right_label = QLabel()
        main_layout.addWidget(self.left_label)
        
        self.field_page = QWidget()
        self.battle_page = QWidget()
        self.stacked_widget = QStackedWidget()

        self.unit_layout = QGridLayout()
        self.field_page.setLayout(self.unit_layout)
        self.battle_layout = QGridLayout()
        self.battle_page.setLayout(self.battle_layout)

        self.stacked_widget.addWidget(self.field_page)
        self.stacked_widget.addWidget(self.battle_page)

        self.stacked_widget.setCurrentWidget(self.field_page)
    
        self.unit_buttons = [] 
        
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.right_label)
        self.setAcceptDrops(True)  # Accept drops
        self.setLayout(main_layout)

    def clear_button_layout(self):
        """Clear all widgets from self.button_layout"""
        self.unit_buttons.clear()
        while self.unit_layout.count():
            item = self.unit_layout.takeAt(0)  # Take the first item
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData().data("application/json").data().decode("utf-8")
        data = json.loads(data)
        if data['source'] == "shop":
            self.parent.send_command('buy_unit', data['index'])
        else:
            self.parent.send_command('move_unit', data['source'], 'field', data['index'], -1)
        self.parent.refresh_style()
        event.acceptProposedAction()

    def update_state(self, data):
        self.clear_button_layout()
        unit_list = data['units']
        max_units = data['max_units']
        unit_count = len([unit for unit in unit_list if unit is not None])
        self.left_label.setText(f"Field\n( {unit_count} / {max_units} )")
        for index in range(len(unit_list)):
            button = QPushButton()
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #cccccc;
                    color: white;
                }}
            """)
            self.unit_layout.addWidget(button, index // 7, index % 7)
        for index, unit in enumerate(unit_list):
            name = unit_to_text(unit)
            button = DraggableLabel(self, name, 'field', index, unit is not None)
            button.clicked.connect(lambda _, i=index: self.parent.view_unit('field', i))
            self.unit_layout.addWidget(button, index // 7 + 4, index % 7)
            self.unit_buttons.append(button) 
            if unit is not None:
                color = self.color_map[unit['cost']]
                hover_color = self.hover_color_map[unit['cost']]
            else:
                color = "#eeeeee"
                hover_color = "#eeeeee"
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
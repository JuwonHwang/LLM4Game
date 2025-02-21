from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QProgressBar
from ..game_ui.util import unit_to_text
from ..baseWidget import BaseWidget

class GameStateWidget(BaseWidget):
    def __init__(self, parent):
        super().__init__("client/game_ui/game_styles.qss")
        self.parent = parent
        main_layout = QHBoxLayout()

        self.state_label = QLabel()
        self.round_label = QLabel()
        self.state_timer = QProgressBar(self)
        self.state_timer.setMinimum(0)  # 최소값
        self.state_timer.setMaximum(1)  # 최대값
        self.state_timer.setValue(0)  # 초기값 설정

        main_layout.addWidget(self.round_label)
        main_layout.addWidget(self.state_label)
        main_layout.addWidget(self.state_timer)

        self.setLayout(main_layout)
                
    def update_state(self, data):
        # print(data['time'])
        self.round_label.setText(f"{data['round']}")
        self.state_label.setText(f"{data['current_state']}")
        self.state_timer.setValue(int(data['time'] * 60))
        self.state_timer.setMaximum(data['state_time'] * 60)
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QProgressBar,
    QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt
from ..game_ui.util import unit_to_text


class BattleUnitWidget(QWidget):
    def __init__(self, unit, color, hover_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = unit

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # 버튼 생성
        self.button = QPushButton(unit_to_text(unit) if unit else "")
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        layout.addWidget(self.button)
        self.health_bar = QProgressBar()
        health_bar_color = '#52a332' if unit and unit['team'] == 'home' else '#a35232'
        self.health_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 4px;
                font-size: 8px;
                height: 10px;
                color: black;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {health_bar_color};
            }}
        """)
        self.health_bar.setTextVisible(True)
        self.health_bar.setFormat('%v/%m')
        if unit:
            # 체력 바 생성
            self.health_bar.setRange(0, int(unit['status']['max_hp']) if unit else 100)
            self.health_bar.setValue(int(unit['status']['hp']) if unit else 0)
        else:
            self.health_bar.setRange(0, 100)
            self.health_bar.setValue(0)
            self.health_bar.setVisible(False)
        layout.addWidget(self.health_bar)
        # 전체 위젯의 스타일 설정
        self.setStyleSheet("background-color: transparent;")
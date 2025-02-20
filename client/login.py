import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget, QFormLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from .baseWidget import BaseWidget

class LoginScreen(BaseWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 타이틀
        title_label = QLabel("🎮 Welcome to py-TFT!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 입력 필드
        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setText("test")
        form_layout.addRow("Username:", self.username_input)

        # 로그인 버튼
        self.login_button = QPushButton("🔑 Login")
        self.login_button.clicked.connect(self.login)

        # 위젯 추가
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)

        
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        if username:
            print(f"Logging in as {username}...")
            if self.parent.socket_thread.sio.connected:
                self.parent.run_async(self.parent.socket_thread.send_command("login", username))
                self.parent.stacked_widget.setCurrentWidget(self.parent.home_screen)
        else:
            print("Please enter a username")

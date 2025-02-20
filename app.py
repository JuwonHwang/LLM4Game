import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from client import SocketThread, GameScreen, HomeScreen, LobbyScreen, LoginScreen

# Function to load URL from a text file
def load_server_url(filename=".server"):
    try:
        with open(filename, "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("⚠ config.txt not found. Using default URL.")
        return "http://localhost:5000"

SERVER_URL = load_server_url()

# ===========================
# 🚀 5️⃣ 메인 UI 컨트롤러
# ===========================
class GameUI(QWidget):
    def __init__(self, loop):
        super().__init__()
        
        self.setWindowTitle("py-TFT-app")
        emoji = "🎮"
        pixmap = self.emoji_to_pixmap(emoji, size=48)
        icon = QIcon(pixmap)
        self.setWindowIcon(icon)
        
        self.loop = loop  # PyQt에서 이벤트 루프를 저장
        
        self.socket_thread = SocketThread(loop, SERVER_URL)
        self.socket_thread.update_ui.connect(self.update_interface)
        self.socket_thread.start()

        self.stacked_widget = QStackedWidget()
        self.login_screen = LoginScreen(self)
        self.home_screen = HomeScreen(self)
        self.lobby_screen = LobbyScreen(self)
        self.game_screen = GameScreen(self)
        
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.lobby_screen)
        self.stacked_widget.addWidget(self.game_screen)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def emoji_to_pixmap(self, emoji, size=64):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        font = QFont("Arial", size - 10)  # 폰트 크기 조절
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)  # 이모지 그리기
        painter.end()

        return pixmap

    def update_interface(self, data):
        # print("UI:", data)
        if "game" in data.keys():
            self.game_screen.update_state(data['game'])
            if len(data['game'].keys()) > 0:
                self.stacked_widget.setCurrentWidget(self.game_screen)
        if "lobby" in data.keys():
            self.lobby_screen.update_state(data['lobby'])
        if "home" in data.keys():
            self.home_screen.update_state(data["home"])
        if "user" in data.keys():
            pass

    def run_async(self, coroutine):
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = QApplication(sys.argv)
    game_ui = GameUI(loop) 
    game_ui.show()
    sys.exit(app.exec())

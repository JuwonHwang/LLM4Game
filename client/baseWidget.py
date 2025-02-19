import sys
import asyncio
import socketio
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QLineEdit, QHBoxLayout, QStackedWidget, QFormLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


class BaseWidget(QWidget):
    def __init__(self, stylesheet_path="client/styles.qss"):
        super().__init__()
        self.load_stylesheet(stylesheet_path)
            
    def load_stylesheet(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
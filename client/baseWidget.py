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
        self.color_map = [
            "#A4A4A4",  
            "#413a41",  
            "#173f29",  
            "#3498db",  
            "#9b59b6",  
            "#f1c40f"   
        ]
        self.hover_color_map = [
            "#A4A4A4",  
            "#615a61",  
            "#375f49",  
            "#5dade2",  
            "#af7ac5",  
            "#f4d03f"   
        ]
            
    def load_stylesheet(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
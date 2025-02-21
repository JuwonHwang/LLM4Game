from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QEvent
from PyQt6.QtGui import QDrag, QPixmap, QPainter
import json

class DraggableLabel(QPushButton):
    def __init__(self, parent, text, source='bench', index=-1, dragable=True):
        super().__init__(text)
        self.parent = parent
        self.source = source
        self.index = index
        self.dragable = dragable
        self.setAcceptDrops(True)  # Accept drops
        # self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragable:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            json_data = json.dumps({'source': self.source, 'index': self.index}).encode("utf-8")
            mime_data.setData("application/json", QByteArray(json_data))
            drag.setMimeData(mime_data)

            # Create a pixmap of the label to show while dragging
            pixmap = self.create_drag_pixmap()
            drag.setPixmap(pixmap)

            # Set the cursor position relative to the dragged pixmap
            drag.setHotSpot(event.position().toPoint() - self.rect().topLeft())

            drag.exec(Qt.DropAction.MoveAction)

    def create_drag_pixmap(self):
        """Create a semi-transparent pixmap of the label"""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background
        painter = QPainter(pixmap)
        painter.setOpacity(0.5)
        self.render(painter)  # Render the label onto the pixmap
        painter.end()
        return pixmap

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData().data("application/json").data().decode("utf-8")
        data = json.loads(data)
        data["target_index"] = self.index
        self.parent.parent.refresh_style()
        self.parent.dropped(data)
        event.acceptProposedAction()
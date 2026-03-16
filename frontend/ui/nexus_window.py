from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import threading

from backend.main_engine import start_nexus
from frontend.ui.orb_widget import OrbWidget


class NexusWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NEXUS")

        self.setFixedSize(220, 220)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        self.old_pos = None

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()

        self.title = QLabel("NEXUS")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Idle")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.orb = OrbWidget()
        self.orb.setFixedSize(150, 150)

        layout.addWidget(self.title)
        layout.addWidget(self.orb)
        layout.addWidget(self.status)

        self.setLayout(layout)

        self.orb.mousePressEvent = self.start_listening

    def start_listening(self, event):

        self.status.setText("Listening...")

        thread = threading.Thread(target=start_nexus)
        thread.start()

    # Make window draggable
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):

        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()
from backend.speech.preferences import SpeechPreferences
from frontend.ui.speech_settings import SpeechSettingsDialog
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from backend.assistant_session import AssistantSession

from backend.main_engine import start_nexus
from frontend.ui.orb_widget import OrbWidget


class NexusWindow(QWidget):
    state_changed = pyqtSignal(str)
    session_error = pyqtSignal(str)
    session_finished = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NEXUS")

        self.setFixedSize(280, 400)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        self.old_pos = None

        self._session = None
        self._failed = False
        self.state_changed.connect(self._on_state)
        self.session_error.connect(self._on_error)
        self.session_finished.connect(self._on_finished)
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
        layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.status)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_listening)
        layout.addWidget(self.stop_button)
        self.settings_button = QPushButton("Speech settings")
        self.settings_button.clicked.connect(self.open_speech_settings)
        layout.addWidget(self.settings_button)
        self.error_message = QLabel("")
        self.error_message.setWordWrap(True)
        self.error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_message)

        self.setLayout(layout)

        self.orb.mousePressEvent = self.start_listening

    def start_listening(self, event=None):
        # Keep this session until its queued completion reaches the UI thread.
        if self._session is not None:
            return
        try:
            SpeechPreferences.from_environment().validate()
        except ValueError as error:
            self._on_error(str(error))
            return
        self._failed = False
        self.error_message.clear()
        self.status.setText("Starting")
        self.stop_button.setEnabled(True)
        self.settings_button.setEnabled(False)
        self._session = AssistantSession(
            start_nexus, self.state_changed.emit,
            self.session_error.emit, self.session_finished.emit,
        )
        self._session.start()

    def open_speech_settings(self):
        if self._session is None:
            SpeechSettingsDialog(self).exec()

    def stop_listening(self):
        if self._session is not None:
            self._session.stop()
            self.status.setText("Stopping...")
            self.stop_button.setEnabled(False)

    def _on_state(self, state):
        if self._session is not None and not self._session.stop_event.is_set():
            self.status.setText(state)

    def _on_error(self, message):
        self._failed = True
        self.status.setText("Error")
        self.error_message.setText(message)

    def _on_finished(self):
        self._session = None
        self.stop_button.setEnabled(False)
        self.settings_button.setEnabled(True)
        if not self._failed:
            self.status.setText("Idle")

    def closeEvent(self, event):
        self.stop_listening()
        super().closeEvent(event)

    # Make window draggable
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):

        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()
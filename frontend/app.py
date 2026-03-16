import sys
from PyQt6.QtWidgets import QApplication
from frontend.ui.nexus_window import NexusWindow


def run_ui():

    app = QApplication(sys.argv)

    window = NexusWindow()
    window.show()

    sys.exit(app.exec())
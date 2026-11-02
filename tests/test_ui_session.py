"""Real Qt checks run when PyQt6 is installed; no models or audio are loaded."""
import importlib.util
import os
import threading
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HAS_QT = importlib.util.find_spec("PyQt6") is not None


@unittest.skipUnless(HAS_QT, "PyQt6 is not installed")
class UiSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        import frontend.ui.nexus_window as ui
        self.ui = ui
        self.window = ui.NexusWindow()
        self.entry = "start_karna" if hasattr(ui, "start_karna") else "start_nexus"

    def tearDown(self):
        if self.window._session is not None:
            self.window._session.stop()
            self.window._session.thread.join(1)
        self.app.processEvents()
        self.window.close()

    def test_repeated_click_stop_and_restart(self):
        started = threading.Event()
        def run(stop, state):
            state("Listening")
            started.set()
            stop.wait(2)
        with patch.object(self.ui, self.entry, run):
            self.window.start_listening()
            self.assertTrue(started.wait(1))
            first = self.window._session
            self.window.start_listening()
            self.assertIs(self.window._session, first)
            self.app.processEvents()
            self.assertEqual(self.window.status.text(), "Listening")
            self.window.stop_button.click()
            self.assertEqual(self.window.status.text(), "Stopping...")
            first.thread.join(1)
            self.app.processEvents()
            self.assertIsNone(self.window._session)
            self.assertEqual(self.window.status.text(), "Idle")
            self.assertFalse(self.window.stop_button.isEnabled())
            self.window.start_listening()
            self.assertIsNotNone(self.window._session)

    def test_worker_failure_stays_visible_and_allows_retry(self):
        def fail(stop, state):
            raise RuntimeError("private-secret")
        with patch.object(self.ui, self.entry, fail):
            self.window.start_listening()
            self.window._session.thread.join(1)
            self.app.processEvents()
            self.assertEqual(self.window.status.text(), "Error")
            self.assertNotIn("private-secret", self.window.error_message.text())
            self.assertTrue(self.window.error_message.text())
            self.assertIsNone(self.window._session)

    def test_close_requests_stop(self):
        def run(stop, state):
            stop.wait(2)
        with patch.object(self.ui, self.entry, run):
            self.window.start_listening()
            session = self.window._session
            self.window.close()
            session.thread.join(1)
            self.assertTrue(session.stop_event.is_set())
            self.assertFalse(session.thread.is_alive())

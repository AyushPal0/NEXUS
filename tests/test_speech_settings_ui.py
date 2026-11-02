import importlib.util
import os
import threading
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HAS_QT = importlib.util.find_spec("PyQt6") is not None


@unittest.skipUnless(HAS_QT, "PyQt6 is not installed")
class SpeechSettingsUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from PyQt6.QtCore import QSettings
        from frontend.ui.speech_settings import SpeechSettingsDialog
        self.env = patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.store = Mock()
        self.store.status.return_value = QSettings.Status.NoError
        self.dialog = SpeechSettingsDialog(store=self.store)

    def tearDown(self):
        self.dialog.close()
        self.env.stop()

    def azure(self):
        self.dialog.provider.setCurrentIndex(1)
        self.dialog.region.setText("eastus")
        self.dialog.key.setText("private-key")

    def test_save_persists_preferences_but_not_key(self):
        self.azure()
        self.dialog.save()
        saved = dict(call.args for call in self.store.setValue.call_args_list)
        self.assertEqual(set(saved), {"provider", "region", "language", "voice"})
        self.assertNotIn("private-key", repr(saved))
        self.assertEqual(os.environ["AZURE_SPEECH_KEY"], "private-key")
        self.assertEqual(os.environ["NEXUS_SPEECH_PROVIDER"], "azure")
        self.assertEqual(self.dialog.key.text(), "")
        self.assertEqual(self.dialog.result(), self.dialog.DialogCode.Accepted)

    def test_cancel_does_not_apply_or_persist(self):
        before = dict(os.environ)
        self.azure()
        self.dialog.reject()
        self.assertEqual(dict(os.environ), before)
        self.store.setValue.assert_not_called()
        self.assertEqual(self.dialog.key.text(), "")

    def test_missing_credentials_keep_dialog_open(self):
        self.dialog.provider.setCurrentIndex(1)
        self.dialog.save()
        self.assertIn("Azure key and region", self.dialog.message.text())
        self.store.setValue.assert_not_called()
        self.assertNotIn("NEXUS_SPEECH_PROVIDER", os.environ)

    def test_blank_key_retains_environment_key(self):
        os.environ["AZURE_SPEECH_KEY"] = "existing-key"
        self.dialog.provider.setCurrentIndex(1)
        self.dialog.region.setText("eastus")
        self.dialog.save()
        self.assertEqual(os.environ["AZURE_SPEECH_KEY"], "existing-key")

    def test_save_failure_leaves_active_configuration_unchanged(self):
        from PyQt6.QtCore import QSettings
        self.azure()
        before = dict(os.environ)
        self.store.status.return_value = QSettings.Status.AccessError
        self.dialog.save()
        self.assertEqual(dict(os.environ), before)
        self.assertIn("Could not save", self.dialog.message.text())

    def test_startup_loads_saved_preferences_with_shell_precedence(self):
        from frontend.ui.speech_settings import initialize_speech_preferences
        saved = {"provider": "azure", "region": "eastus", "language": "en-IN", "voice": "en-IN-NeerjaNeural"}
        self.store.value.side_effect = lambda key, default=None: saved.get(key, default)
        os.environ["AZURE_SPEECH_REGION"] = "centralindia"
        initialize_speech_preferences(self.store)
        self.assertEqual(os.environ["NEXUS_SPEECH_PROVIDER"], "azure")
        self.assertEqual(os.environ["AZURE_SPEECH_REGION"], "centralindia")
        self.assertNotIn("AZURE_SPEECH_KEY", os.environ)
        self.assertEqual({call.args[0] for call in self.store.value.call_args_list}, set(saved))

    def test_main_window_blocks_unconfigured_azure(self):
        import frontend.ui.nexus_window as ui
        window = ui.NexusWindow()
        try:
            os.environ["NEXUS_SPEECH_PROVIDER"] = "azure"
            with patch.object(ui, "AssistantSession") as session:
                window.start_listening()
                session.assert_not_called()
            self.assertEqual(window.status.text(), "Error")
            self.assertIn("Speech settings", window.error_message.text())
            self.assertTrue(window.settings_button.isEnabled())
        finally:
            window.close()

    def test_settings_disabled_until_session_cleanup(self):
        import frontend.ui.nexus_window as ui
        window = ui.NexusWindow()
        def run(stop, state):
            stop.wait(2)
        name = "start_karna" if hasattr(ui, "start_karna") else "start_nexus"
        try:
            with patch.object(ui, name, run), patch.object(ui, "SpeechSettingsDialog") as dialog:
                window.start_listening()
                session = window._session
                self.assertFalse(window.settings_button.isEnabled())
                window.open_speech_settings()
                dialog.assert_not_called()
                window.stop_listening()
                self.assertFalse(window.settings_button.isEnabled())
                session.thread.join(1)
                self.app.processEvents()
                self.assertTrue(window.settings_button.isEnabled())
                window.open_speech_settings()
                dialog.return_value.exec.assert_called_once()
        finally:
            if window._session is not None:
                window._session.stop()
                window._session.thread.join(1)
                self.app.processEvents()
            window.close()

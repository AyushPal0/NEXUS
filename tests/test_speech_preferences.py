import os
import unittest
from unittest.mock import patch
from backend.speech.preferences import SpeechPreferences


class SpeechPreferencesTests(unittest.TestCase):
    def test_defaults_require_no_azure_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            preferences = SpeechPreferences.from_environment()
            preferences.validate()
            self.assertEqual(preferences.provider, "default")

    def test_missing_key_and_region_are_actionable(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Azure key and region"):
                SpeechPreferences(provider="azure").validate()

    def test_valid_azure_preferences_apply_without_key_in_model(self):
        with patch.dict(os.environ, {}, clear=True):
            preferences = SpeechPreferences("azure", "centralindia", "hi-IN", "hi-IN-SwaraNeural")
            preferences.apply("private-key")
            self.assertEqual(os.environ["AZURE_SPEECH_KEY"], "private-key")
            self.assertEqual(os.environ["AZURE_SPEECH_LANGUAGE"], "hi-IN")
            self.assertEqual(SpeechPreferences.from_environment(), preferences)
            self.assertNotIn("private-key", repr(preferences))

    def test_invalid_configuration_does_not_mutate_environment(self):
        with patch.dict(os.environ, {}, clear=True):
            before = dict(os.environ)
            with self.assertRaises(ValueError):
                SpeechPreferences("azure", "bad region").apply("private-key")
            self.assertEqual(dict(os.environ), before)

    def test_validation_excludes_key_from_error(self):
        with self.assertRaises(ValueError) as error:
            SpeechPreferences("azure", "eastus", "invalid", "voice").validate("private-key")
        self.assertNotIn("private-key", str(error.exception))

    def test_provider_switch_preserves_existing_session_key(self):
        with patch.dict(os.environ, {"AZURE_SPEECH_KEY": "session-key"}, clear=True):
            SpeechPreferences().apply()
            self.assertEqual(os.environ["AZURE_SPEECH_KEY"], "session-key")

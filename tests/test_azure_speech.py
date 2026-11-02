import importlib
import os
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

class AzureSpeechTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"AZURE_SPEECH_KEY": "test-key", "AZURE_SPEECH_REGION": "test-region"}, clear=True)
        self.env.start()
        self.sdk = ModuleType("azure.cognitiveservices.speech")
        self.sdk.SpeechConfig = Mock()
        self.sdk.audio = SimpleNamespace(AudioConfig=Mock(), AudioOutputConfig=Mock())
        self.sdk.ResultReason = SimpleNamespace(RecognizedSpeech=1, NoMatch=2, SynthesizingAudioCompleted=3, Canceled=4)
        self.sdk.SpeechRecognizer = Mock()
        self.sdk.SpeechSynthesizer = Mock()
        azure = ModuleType("azure")
        cognitive = ModuleType("azure.cognitiveservices")
        azure.cognitiveservices = cognitive
        cognitive.speech = self.sdk
        self.modules = patch.dict(sys.modules, {"azure": azure, "azure.cognitiveservices": cognitive, "azure.cognitiveservices.speech": self.sdk})
        self.modules.start()
        from backend.speech.azure_provider import AzureSpeechProvider
        self.provider_type = AzureSpeechProvider

    def tearDown(self):
        self.modules.stop()
        self.env.stop()

    def test_credentials_required(self):
        del os.environ["AZURE_SPEECH_KEY"]
        with self.assertRaisesRegex(RuntimeError, "AZURE_SPEECH_KEY"):
            self.provider_type()

    def test_recognized_text_normalized(self):
        self.sdk.SpeechRecognizer.return_value.recognize_once_async.return_value.get.return_value = SimpleNamespace(reason=1, text=" Open YouTube. ")
        self.assertEqual(self.provider_type().listen(), "open youtube.")
        self.sdk.SpeechConfig.assert_called_once_with(subscription="test-key", region="test-region")

    def test_no_match_is_empty(self):
        self.sdk.SpeechRecognizer.return_value.recognize_once_async.return_value.get.return_value = SimpleNamespace(reason=2)
        self.assertEqual(self.provider_type().listen(), "")

    def test_cancellation_does_not_expose_key(self):
        self.sdk.SpeechRecognizer.return_value.recognize_once_async.return_value.get.return_value = SimpleNamespace(reason=4)
        with self.assertRaises(RuntimeError) as error:
            self.provider_type().listen()
        self.assertNotIn("test-key", str(error.exception))

    def test_synthesis_success_and_failure(self):
        result = self.sdk.SpeechSynthesizer.return_value.speak_text_async.return_value.get
        result.return_value = SimpleNamespace(reason=3)
        self.provider_type().speak("Hello")
        self.sdk.SpeechSynthesizer.return_value.speak_text_async.assert_called_once_with("Hello")
        result.return_value = SimpleNamespace(reason=4)
        with self.assertRaises(RuntimeError):
            self.provider_type().speak("Hello")

    def test_default_provider_does_not_initialize_azure_or_tts_on_import(self):
        with patch.dict(sys.modules, {"speech_recognition": Mock(), "pyttsx3": Mock()}):
            sys.modules.pop("backend.speech.speech_engine", None)
            engine = importlib.import_module("backend.speech.speech_engine")
            self.assertIsNone(engine._azure_provider())
            self.assertIsNone(engine.engine)
            self.sdk.SpeechConfig.assert_not_called()
            sys.modules.pop("backend.speech.speech_engine", None)

    def test_invalid_provider_is_explicit(self):
        with patch.dict(sys.modules, {"speech_recognition": Mock(), "pyttsx3": Mock()}):
            sys.modules.pop("backend.speech.speech_engine", None)
            engine = importlib.import_module("backend.speech.speech_engine")
            os.environ["NEXUS_SPEECH_PROVIDER"] = "typo"
            with self.assertRaisesRegex(RuntimeError, "default or azure"):
                engine._azure_provider()
            sys.modules.pop("backend.speech.speech_engine", None)

    def test_selected_provider_dispatches_and_is_cached(self):
        with patch.dict(sys.modules, {"speech_recognition": Mock(), "pyttsx3": Mock()}):
            sys.modules.pop("backend.speech.speech_engine", None)
            engine = importlib.import_module("backend.speech.speech_engine")
            os.environ["NEXUS_SPEECH_PROVIDER"] = "azure"
            with patch("backend.speech.azure_provider.AzureSpeechProvider") as factory:
                provider = factory.return_value
                provider.listen.return_value = "open youtube"
                self.assertEqual(engine.listen(), "open youtube")
                engine.speak("Hello")
                factory.assert_called_once()
                provider.speak.assert_called_once_with("Hello")
            sys.modules.pop("backend.speech.speech_engine", None)

    def test_language_and_voice_configuration(self):
        os.environ["AZURE_SPEECH_LANGUAGE"] = "hi-IN"
        os.environ["AZURE_SPEECH_VOICE"] = "hi-IN-SwaraNeural"
        provider = self.provider_type()
        self.assertEqual(provider.config.speech_recognition_language, "hi-IN")
        self.assertEqual(provider.config.speech_synthesis_voice_name, "hi-IN-SwaraNeural")

    def test_missing_sdk_has_installation_hint(self):
        with patch.dict(sys.modules, {"azure.cognitiveservices.speech": None}):
            with self.assertRaisesRegex(RuntimeError, "requirements-azure.txt"):
                self.provider_type()

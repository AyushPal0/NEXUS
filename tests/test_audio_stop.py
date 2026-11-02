import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from backend.speech.cancellable_audio import listen
from backend.speech import azure_session


class Signal:
    def __init__(self):
        self.handlers = []

    def connect(self, fn):
        self.handlers.append(fn)

    def disconnect(self, fn):
        self.handlers.remove(fn)

    def emit(self, event=None):
        for handler in list(self.handlers):
            handler(event)


class AudioStopTests(unittest.TestCase):
    def test_default_capture_stop_closes_microphone(self):
        stop = threading.Event()
        source = SimpleNamespace(SAMPLE_RATE=16000, SAMPLE_WIDTH=2)
        mic = Mock()
        mic.__enter__ = Mock(return_value=source)
        mic.__exit__ = Mock(return_value=False)
        sr = SimpleNamespace(Microphone=Mock(return_value=mic), WaitTimeoutError=TimeoutError)
        recognizer = Mock()

        def chunks(*args, **kwargs):
            yield SimpleNamespace(frame_data=b"first")
            stop.set()
            yield SimpleNamespace(frame_data=b"second")
        recognizer.listen.side_effect = chunks
        self.assertEqual(listen(recognizer, sr, stop), "")
        mic.__exit__.assert_called_once()
        recognizer.recognize_google.assert_not_called()

    def test_default_capture_can_stop_while_waiting_for_speech(self):
        stop = threading.Event()
        mic = Mock()
        mic.__enter__ = Mock(return_value=SimpleNamespace(SAMPLE_RATE=16000, SAMPLE_WIDTH=2))
        mic.__exit__ = Mock(return_value=False)
        sr = SimpleNamespace(Microphone=Mock(return_value=mic), WaitTimeoutError=TimeoutError)
        recognizer = Mock()
        def silence(*args, **kwargs):
            stop.set()
            raise TimeoutError()
        recognizer.listen.side_effect = silence
        self.assertEqual(listen(recognizer, sr, stop), "")
        mic.__exit__.assert_called_once()

    def provider(self):
        recognizer = Mock()
        for name in ("recognized", "canceled", "session_stopped"):
            setattr(recognizer, name, Signal())
        synth = Mock()
        synth.synthesis_completed = Signal()
        synth.synthesis_canceled = Signal()
        sdk = SimpleNamespace(
            SpeechRecognizer=Mock(return_value=recognizer),
            SpeechSynthesizer=Mock(return_value=synth),
            audio=SimpleNamespace(AudioConfig=Mock(), AudioOutputConfig=Mock()),
            ResultReason=SimpleNamespace(RecognizedSpeech=1, NoMatch=2, SynthesizingAudioCompleted=3),
        )
        return SimpleNamespace(sdk=sdk, config=Mock()), recognizer, synth

    def test_azure_stop_terminates_recognizer_and_disconnects_callbacks(self):
        provider, recognizer, _ = self.provider()
        stop = threading.Event()
        recognizer.start_continuous_recognition_async.side_effect = lambda: (stop.set() or Mock())
        self.assertEqual(azure_session.listen(provider, stop), "")
        recognizer.stop_continuous_recognition_async.return_value.get.assert_called_once()
        self.assertEqual(recognizer.recognized.handlers, [])
        self.assertEqual(recognizer.canceled.handlers, [])

    def test_azure_success_also_stops_microphone(self):
        provider, recognizer, _ = self.provider()
        def start():
            recognizer.recognized.emit(SimpleNamespace(result=SimpleNamespace(reason=1, text=" Open YouTube ")))
            return Mock()
        recognizer.start_continuous_recognition_async.side_effect = start
        self.assertEqual(azure_session.listen(provider, threading.Event()), "open youtube")
        recognizer.stop_continuous_recognition_async.return_value.get.assert_called_once()

    def test_azure_synthesis_stop_calls_sdk_stop(self):
        provider, _, synth = self.provider()
        stop = threading.Event()
        future = Mock()
        def speak(text):
            stop.set()
            return future
        synth.speak_text_async.side_effect = speak
        azure_session.speak(provider, "Hello", stop)
        synth.stop_speaking_async.return_value.get.assert_called_once()
        self.assertEqual(synth.synthesis_completed.handlers, [])

    def test_azure_start_failure_still_cleans_up(self):
        provider, recognizer, _ = self.provider()
        recognizer.start_continuous_recognition_async.side_effect = RuntimeError("SDK failed")
        with self.assertRaises(RuntimeError):
            azure_session.listen(provider, threading.Event())
        recognizer.stop_continuous_recognition_async.return_value.get.assert_called_once()
        self.assertEqual(recognizer.recognized.handlers, [])

    def test_default_playback_stop_ends_loop_and_releases_engine(self):
        import importlib
        import sys
        from unittest.mock import patch
        stop = threading.Event()
        tts = Mock()
        tts.isBusy.return_value = True
        tts.iterate.side_effect = stop.set
        with patch.dict(sys.modules, {"speech_recognition": Mock(), "pyttsx3": Mock()}):
            sys.modules.pop("backend.speech.speech_engine", None)
            engine = importlib.import_module("backend.speech.speech_engine")
            engine.engine = tts
            with patch.dict("os.environ", {"NEXUS_SPEECH_PROVIDER": "default"}):
                engine.speak("Hello", stop_event=stop)
            tts.stop.assert_called_once()
            tts.endLoop.assert_called_once()
            engine.close()
            self.assertIsNone(engine.engine)
            sys.modules.pop("backend.speech.speech_engine", None)

    def test_azure_timeout_returns_empty_after_cleanup_event(self):
        from unittest.mock import patch
        provider, recognizer, _ = self.provider()
        def stop():
            recognizer.session_stopped.emit()
            return Mock()
        recognizer.stop_continuous_recognition_async.side_effect = stop
        with patch.object(azure_session.time, "monotonic", side_effect=[0, 31]):
            self.assertEqual(azure_session.listen(provider, threading.Event()), "")
        self.assertEqual(recognizer.session_stopped.handlers, [])

    def test_wake_word_stop_closes_stream(self):
        import importlib
        import sys
        from unittest.mock import patch
        stop = threading.Event()
        stream = Mock()
        stream.__enter__ = Mock()
        stream.__exit__ = Mock(return_value=False)
        sound = SimpleNamespace(RawInputStream=Mock(return_value=stream))
        with patch.dict(sys.modules, {"sounddevice": sound, "vosk": Mock()}):
            sys.modules.pop("backend.speech.wake_word", None)
            wake = importlib.import_module("backend.speech.wake_word")
            self.assertIsNone(wake.model)
            def empty_queue(**kwargs):
                stop.set()
                raise wake.queue.Empty()
            wake.q.get = Mock(side_effect=empty_queue)
            self.assertFalse(wake.listen_for_wake_word(stop_event=stop))
            stream.__exit__.assert_called_once()
            sys.modules.pop("backend.speech.wake_word", None)

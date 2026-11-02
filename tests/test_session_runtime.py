import sys
import threading
import unittest
from types import ModuleType
from unittest.mock import Mock, patch
from backend.assistant_runtime import run_session
import backend.speech


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.stop = threading.Event()
        self.states = []
        self.speech = Mock()
        self.speech.listen.return_value = "open youtube"
        self.wake = Mock(return_value=True)
        self.handler = Mock(return_value=False)
        modules = {}
        for name, bindings in {
            "backend.speech.wake_word": {"listen_for_wake_word": self.wake},
            "backend.brain.command_handler": {"handle_command": self.handler},
        }.items():
            modules[name] = ModuleType(name)
            modules[name].__dict__.update(bindings)
        self.patches = [patch.dict(sys.modules, modules),
                        patch.object(backend.speech, "speech_engine", self.speech, create=True)]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

    def test_states_and_resources_on_normal_exit(self):
        run_session(self.stop, self.states.append)
        self.assertEqual(self.states, ["Starting", "Speaking", "Thinking", "Waiting for wake word", "Speaking", "Thinking", "Listening", "Thinking"])
        self.speech.close.assert_called_once()
        self.handler.assert_called_once()
        self.assertIs(self.handler.call_args.kwargs["stop_event"], self.stop)

    def test_stop_during_wake_skips_recognition(self):
        def stop_wake(**kwargs):
            self.stop.set()
            return False
        self.wake.side_effect = stop_wake
        run_session(self.stop, self.states.append)
        self.speech.listen.assert_not_called()
        self.handler.assert_not_called()
        self.speech.close.assert_called_once()

    def test_recognition_error_still_cleans_up(self):
        self.speech.listen.side_effect = RuntimeError("network")
        with self.assertRaises(RuntimeError):
            run_session(self.stop, self.states.append)
        self.speech.close.assert_called_once()

    def test_stop_during_recognition_skips_actions(self):
        def listen(**kwargs):
            self.stop.set()
            return "open youtube"
        self.speech.listen.side_effect = listen
        run_session(self.stop, self.states.append)
        self.handler.assert_not_called()
        self.speech.close.assert_called_once()

    def test_pre_stopped_session_does_not_open_audio(self):
        self.stop.set()
        run_session(self.stop, self.states.append)
        self.speech.speak.assert_not_called()

"""Session lifecycle tests use real workers without models or audio devices."""
import threading
import unittest
from backend.assistant_session import AssistantSession


class ListenerTests(unittest.TestCase):
    def test_stop_reaches_worker_and_completion_runs_once(self):
        started = threading.Event()
        finished = []
        states = []

        def run(stop, on_state):
            on_state("Listening")
            started.set()
            self.assertTrue(stop.wait(1))

        errors = []
        session = AssistantSession(run, states.append, errors.append, lambda: finished.append(True))
        session.start()
        self.assertTrue(started.wait(1))
        session.stop()
        session.thread.join(1)
        self.assertFalse(session.thread.is_alive())
        self.assertEqual(states, ["Listening"])
        self.assertEqual(errors, [])
        self.assertEqual(finished, [True])

    def test_error_is_visible_without_exception_secrets(self):
        def run(stop, on_state):
            raise RuntimeError("secret-resource-key")

        errors, finished = [], []
        session = AssistantSession(run, lambda state: None, errors.append, lambda: finished.append(True))
        session.start()
        session.thread.join(1)
        self.assertEqual(len(errors), 1)
        self.assertIn("speech settings", errors[0])
        self.assertNotIn("secret-resource-key", errors[0])
        self.assertEqual(finished, [True])

    def test_canceled_worker_error_does_not_replace_stopping_state(self):
        def run(stop, on_state):
            stop.set()
            raise RuntimeError("canceled")

        errors = []
        session = AssistantSession(run, lambda state: None, errors.append, lambda: None)
        session.start()
        session.thread.join(1)
        self.assertEqual(errors, [])

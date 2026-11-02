"""One assistant session, with cooperative stop and UI-neutral notifications."""
import threading


class AssistantSession:
    def __init__(self, run, on_state, on_error, on_finished):
        self.stop_event = threading.Event()
        self._run_assistant = run
        self._on_state = on_state
        self._on_error = on_error
        self._on_finished = on_finished
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _run(self):
        try:
            self._run_assistant(self.stop_event, self._on_state)
        except Exception as error:
            if not self.stop_event.is_set():
                if isinstance(error, (ImportError, FileNotFoundError)):
                    message = "Missing dependency or local model. Check the project setup."
                else:
                    message = "Check speech settings, microphone, network, and Ollama."
                # Never copy SDK exceptions or credentials into the interface.
                self._on_error(message)
        finally:
            self._on_finished()

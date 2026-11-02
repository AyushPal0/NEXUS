"""Assistant loop loaded inside the worker, so setup errors reach the UI."""
import threading


class SessionStopped(Exception):
    pass


def run_session(stop_event=None, on_state=None, greeting="Nexus is online"):
    stop_event = stop_event if stop_event is not None else threading.Event()
    on_state = on_state if on_state is not None else lambda state: None
    if stop_event.is_set():
        return
    from backend.speech import speech_engine

    def check_stop():
        if stop_event.is_set():
            raise SessionStopped()

    def say(text):
        check_stop()
        on_state("Speaking")
        speech_engine.speak(text, stop_event=stop_event)
        check_stop()
        on_state("Thinking")

    try:
        on_state("Starting")
        from backend.speech.wake_word import listen_for_wake_word
        from backend.brain.command_handler import handle_command
        check_stop()
        say(greeting)
        while not stop_event.is_set():
            on_state("Waiting for wake word")
            if not listen_for_wake_word(stop_event=stop_event):
                break
            check_stop()
            say("Yes?")
            on_state("Listening")
            command = speech_engine.listen(stop_event=stop_event)
            check_stop()
            if not command:
                continue
            on_state("Thinking")
            if not handle_command(command, say, stop_event=stop_event):
                break
    except SessionStopped:
        pass
    finally:
        speech_engine.close()

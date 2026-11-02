"""Compatibility entry point; dependencies load inside the assistant worker."""
from backend.assistant_runtime import run_session


def start_nexus(stop_event=None, on_state=None):
    return run_session(stop_event, on_state, greeting="Nexus is online")

import speech_recognition as sr
import pyttsx3

# Initialize only the selected provider when it is first used.
engine = None
_azure = None

def _azure_provider():
    import os
    global _azure
    provider = os.environ.get("NEXUS_SPEECH_PROVIDER", "default").strip().lower()
    if provider == "default":
        return None
    if provider != "azure":
        raise RuntimeError("NEXUS_SPEECH_PROVIDER must be default or azure.")
    if _azure is None:
        from backend.speech.azure_provider import AzureSpeechProvider
        _azure = AzureSpeechProvider()
    return _azure

def speak(text, stop_event=None):
    if stop_event is not None and stop_event.is_set():
        return ""
    global engine
    provider = _azure_provider()
    if provider is not None:
        if stop_event is not None:
            return provider.speak(text, stop_event=stop_event)
        return provider.speak(text)
    if engine is None:
        engine = pyttsx3.init()
    if stop_event is not None and stop_event.is_set():
        return
    engine.say(text)
    if stop_event is None:
        engine.runAndWait()
        return
    engine.startLoop(False)
    try:
        while engine.isBusy() and not stop_event.is_set():
            engine.iterate()
            stop_event.wait(0.02)
        if stop_event.is_set():
            engine.stop()
    finally:
        engine.endLoop()

def listen(stop_event=None):
    if stop_event is not None and stop_event.is_set():
        return ""
    provider = _azure_provider()
    if provider is not None:
        if stop_event is not None:
            return provider.listen(stop_event=stop_event)
        return provider.listen()
    recognizer = sr.Recognizer()
    if stop_event is not None:
        from backend.speech.cancellable_audio import listen as listen_cancellable
        return listen_cancellable(recognizer, sr, stop_event)

    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("User:", command)
        return command.lower()

    except:
        return ""

def close():
    """Release worker-owned speech resources before another session starts."""
    global engine, _azure
    try:
        if engine is not None:
            engine.stop()
    finally:
        engine = None
        _azure = None

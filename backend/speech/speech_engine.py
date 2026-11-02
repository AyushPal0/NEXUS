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

def speak(text):
    global engine
    provider = _azure_provider()
    if provider is not None:
        return provider.speak(text)
    if engine is None:
        engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    provider = _azure_provider()
    if provider is not None:
        return provider.listen()
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("User:", command)
        return command.lower()

    except:
        return ""
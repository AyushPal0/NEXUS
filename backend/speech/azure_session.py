"""Cancellable Azure operations using SDK lifecycle events."""
import threading
import time


def listen(provider, stop_event):
    if stop_event.is_set():
        return ""
    sdk = provider.sdk
    recognizer = sdk.SpeechRecognizer(
        speech_config=provider.config,
        audio_config=sdk.audio.AudioConfig(use_default_microphone=True),
    )
    done = threading.Event()
    results = []
    timed_out = False

    def recognized(event):
        results.append(event.result)
        done.set()

    def ended(event):
        done.set()

    recognizer.recognized.connect(recognized)
    recognizer.canceled.connect(ended)
    recognizer.session_stopped.connect(ended)
    try:
        recognizer.start_continuous_recognition_async().get()
        deadline = time.monotonic() + 30
        while not done.wait(0.05):
            if stop_event.is_set():
                break
            if time.monotonic() >= deadline:
                timed_out = True
                break
    finally:
        # Wait for SDK cleanup before permitting a new microphone session.
        recognizer.stop_continuous_recognition_async().get()
        recognizer.recognized.disconnect(recognized)
        recognizer.canceled.disconnect(ended)
        recognizer.session_stopped.disconnect(ended)
    if stop_event.is_set():
        return ""
    if results:
        result = results[0]
        if result.reason == sdk.ResultReason.RecognizedSpeech:
            return result.text.strip().lower()
        if result.reason == sdk.ResultReason.NoMatch:
            return ""
    if timed_out:
        return ""
    raise RuntimeError("Azure speech recognition failed. Check speech settings and network.")


def speak(provider, text, stop_event):
    if stop_event.is_set():
        return
    sdk = provider.sdk
    synthesizer = sdk.SpeechSynthesizer(
        speech_config=provider.config,
        audio_config=sdk.audio.AudioOutputConfig(use_default_speaker=True),
    )
    done = threading.Event()

    def completed(event):
        done.set()

    synthesizer.synthesis_completed.connect(completed)
    synthesizer.synthesis_canceled.connect(completed)
    try:
        result_future = synthesizer.speak_text_async(text)
        deadline = time.monotonic() + 60
        while not done.wait(0.05):
            if stop_event.is_set() or time.monotonic() >= deadline:
                synthesizer.stop_speaking_async().get()
                break
        result = result_future.get()
        if not stop_event.is_set() and result.reason != sdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError("Azure speech synthesis failed. Check speech settings and network.")
    finally:
        synthesizer.synthesis_completed.disconnect(completed)
        synthesizer.synthesis_canceled.disconnect(completed)

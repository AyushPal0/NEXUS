"""Optional Azure Speech adapter; importing it does not open audio devices."""
import os

class AzureSpeechProvider:
    def __init__(self):
        key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
        region = os.environ.get("AZURE_SPEECH_REGION", "").strip()
        if not key or not region:
            raise RuntimeError("Azure speech requires AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.")
        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError as error:
            raise RuntimeError("Install the Azure speech extra: pip install -r requirements-azure.txt") from error
        self.sdk = speechsdk
        self.config = speechsdk.SpeechConfig(subscription=key, region=region)
        self.config.speech_recognition_language = os.environ.get("AZURE_SPEECH_LANGUAGE", "en-US")
        self.config.speech_synthesis_voice_name = os.environ.get("AZURE_SPEECH_VOICE", "en-US-JennyNeural")

    def listen(self, stop_event=None):
        if stop_event is not None:
            from backend.speech.azure_session import listen
            return listen(self, stop_event)
        sdk = self.sdk
        audio = sdk.audio.AudioConfig(use_default_microphone=True)
        recognizer = sdk.SpeechRecognizer(speech_config=self.config, audio_config=audio)
        result = recognizer.recognize_once_async().get()
        if result.reason == sdk.ResultReason.RecognizedSpeech:
            return result.text.strip().lower()
        if result.reason == sdk.ResultReason.NoMatch:
            return ""
        # Do not log cancellation details: they can include service configuration.
        raise RuntimeError("Azure speech recognition failed. Check your credentials, region, network and microphone.")

    def speak(self, text, stop_event=None):
        if stop_event is not None:
            from backend.speech.azure_session import speak
            return speak(self, text, stop_event)
        sdk = self.sdk
        audio = sdk.audio.AudioOutputConfig(use_default_speaker=True)
        synthesizer = sdk.SpeechSynthesizer(speech_config=self.config, audio_config=audio)
        result = synthesizer.speak_text_async(text).get()
        if result.reason != sdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError("Azure speech synthesis failed. Check your credentials, region, network and voice.")

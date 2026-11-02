"""Non-secret speech preferences; credentials are never part of this model."""
from dataclasses import dataclass
import os
import re


@dataclass(frozen=True)
class SpeechPreferences:
    provider: str = "default"
    region: str = ""
    language: str = "en-US"
    voice: str = "en-US-JennyNeural"

    @classmethod
    def from_environment(cls):
        return cls(
            os.environ.get("NEXUS_SPEECH_PROVIDER", "default").strip().lower(),
            os.environ.get("AZURE_SPEECH_REGION", "").strip(),
            os.environ.get("AZURE_SPEECH_LANGUAGE", "en-US").strip(),
            os.environ.get("AZURE_SPEECH_VOICE", "en-US-JennyNeural").strip(),
        )

    def validate(self, key=None):
        if self.provider not in {"default", "azure"}:
            raise ValueError("Choose Default or Azure in Speech settings.")
        if self.provider == "default":
            return
        if key is None:
            key = os.environ.get("AZURE_SPEECH_KEY", "")
        if not key.strip() or not self.region:
            raise ValueError("Set your Azure key and region in Speech settings.")
        if not re.fullmatch(r"[a-z0-9]+", self.region):
            raise ValueError("Use your Azure region code, for example eastus or centralindia.")
        if not re.fullmatch(r"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]+)+", self.language):
            raise ValueError("Use a language code such as en-US, en-IN, or hi-IN.")
        if not re.fullmatch(r"[a-zA-Z0-9-]+", self.voice):
            raise ValueError("Enter an Azure voice name, for example en-US-JennyNeural.")

    def apply(self, key=None):
        self.validate(key)
        os.environ.update({
            "NEXUS_SPEECH_PROVIDER": self.provider,
            "AZURE_SPEECH_REGION": self.region,
            "AZURE_SPEECH_LANGUAGE": self.language,
            "AZURE_SPEECH_VOICE": self.voice,
        })
        if key is not None and key.strip():
            os.environ["AZURE_SPEECH_KEY"] = key.strip()

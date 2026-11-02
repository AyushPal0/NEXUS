"""Speech settings dialog. Only non-secret preferences are persisted."""
import os
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout,
)
from backend.speech.preferences import SpeechPreferences


FIELDS = {
    "provider": "NEXUS_SPEECH_PROVIDER",
    "region": "AZURE_SPEECH_REGION",
    "language": "AZURE_SPEECH_LANGUAGE",
    "voice": "AZURE_SPEECH_VOICE",
}


def settings_store():
    return QSettings("NexusAssistant", "Speech")


def initialize_speech_preferences(store=None):
    """Explicit shell variables override saved preferences at startup."""
    store = settings_store() if store is None else store
    for field, variable in FIELDS.items():
        saved = store.value(field, None)
        if saved is not None and variable not in os.environ:
            os.environ[variable] = str(saved)


class SpeechSettingsDialog(QDialog):
    def __init__(self, parent=None, store=None):
        super().__init__(parent)
        self.store = settings_store() if store is None else store
        self.setWindowTitle("Speech settings")
        self.setMinimumWidth(440)
        current = SpeechPreferences.from_environment()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.provider = QComboBox()
        self.provider.addItem("Default (Google + local voice)", "default")
        self.provider.addItem("Microsoft Azure Speech", "azure")
        self.provider.setCurrentIndex(max(0, self.provider.findData(current.provider)))
        self.region = QLineEdit(current.region)
        self.region.setPlaceholderText("Your resource region, e.g. centralindia")
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.key.setPlaceholderText(
            "Configured for this session; leave blank to keep"
            if os.environ.get("AZURE_SPEECH_KEY", "").strip()
            else "Paste key for this app session only"
        )
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(["en-US", "en-IN", "hi-IN"])
        self.language.setCurrentText(current.language)
        self.voice = QLineEdit(current.voice)
        form.addRow("Provider", self.provider)
        form.addRow("Azure region", self.region)
        form.addRow("Azure key", self.key)
        form.addRow("Recognition language", self.language)
        form.addRow("Azure voice", self.voice)
        layout.addLayout(form)
        self.description = QLabel()
        self.description.setWordWrap(True)
        layout.addWidget(self.description)
        self.readiness = QLabel()
        self.readiness.setWordWrap(True)
        layout.addWidget(self.readiness)
        self.message = QLabel("")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.save)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.provider.currentIndexChanged.connect(self.update_readiness)
        for field in (self.region, self.key, self.voice):
            field.textChanged.connect(self.update_readiness)
        self.language.currentTextChanged.connect(self.update_readiness)
        self.update_readiness()

    def preferences(self):
        return SpeechPreferences(
            self.provider.currentData(), self.region.text().strip(),
            self.language.currentText().strip(), self.voice.text().strip(),
        )

    def effective_key(self):
        return self.key.text().strip() or os.environ.get("AZURE_SPEECH_KEY", "").strip()

    def update_readiness(self):
        azure = self.provider.currentData() == "azure"
        for field in (self.region, self.key, self.language, self.voice):
            field.setEnabled(azure)
        self.description.setText(
            "Azure receives command audio and response text. Internet and an Azure "
            "Speech resource are required; usage may incur charges. Only preferences "
            "are saved. Your key stays in memory for this app session."
            if azure else
            "Default uses Google for command recognition and pyttsx3 for local speech. "
            "The Vosk wake word stays local with either provider."
        )
        try:
            self.preferences().validate(self.effective_key())
        except ValueError as error:
            self.readiness.setText(str(error))
        else:
            self.readiness.setText(
                "Azure configuration complete. Connection and voice availability are untested."
                if azure else "Default provider selected."
            )

    def save(self):
        preferences = self.preferences()
        key = self.effective_key()
        try:
            preferences.validate(key)
        except ValueError as error:
            self.message.setText(str(error))
            return
        for field in FIELDS:
            self.store.setValue(field, getattr(preferences, field))
        self.store.sync()
        if self.store.status() != QSettings.Status.NoError:
            self.message.setText("Could not save preferences. Check local settings permissions.")
            return
        preferences.apply(key)
        self.key.clear()
        self.accept()

    def done(self, result):
        self.key.clear()
        super().done(result)

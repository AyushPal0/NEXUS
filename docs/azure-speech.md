# Optional Microsoft Azure Speech integration

KARNA/NEXUS can use Microsoft's Python Speech SDK for command recognition and
spoken responses. The PyQt6 UI, local Vosk wake-word detector, and Ollama planner
remain in place. The default provider retains Google recognition and pyttsx3.

## In-app speech settings

Click **Speech settings** while the assistant is idle. Choose Microsoft Azure
Speech and enter your resource region, session key, recognition language, and
voice name. Save applies the settings to the next assistant session. The dialog
validates required fields; it does not contact Azure or verify credentials.
Install the optional SDK below before using Azure.

Only provider, region, language, and voice are saved locally through Qt settings
(`NexusAssistant/Speech`, in the Windows user registry). The key is held in the
app process environment and is never written to these settings. After restarting,
enter the key again or supply `AZURE_SPEECH_KEY` in the launching shell. Existing
shell variables override saved preferences at app startup. Cancel leaves the
active configuration unchanged. Settings are disabled while a session is running
or stopping. Changing recognition language does not change the Vosk wake-word
model. Choose a voice supported by Azure for your desired output language.

## Setup on Windows

Use your existing project Python environment and dependencies. From the project
root, install the optional provider:

```powershell
python -m pip install -r requirements-azure.txt
```

Create an Azure Speech resource and obtain its key and region. Azure mode sends
command audio and response text to Azure; it requires internet access and may
incur service charges. Each user supplies their own credentials.

Set variables in the same PowerShell session used to launch the app:

```powershell
$env:NEXUS_SPEECH_PROVIDER = "azure"
$env:AZURE_SPEECH_KEY = "<your-resource-key>"
$env:AZURE_SPEECH_REGION = "<your-resource-region>"
$env:AZURE_SPEECH_LANGUAGE = "en-US"
$env:AZURE_SPEECH_VOICE = "en-US-JennyNeural"
python run_nexus.py
```

`.env.example` documents the variables; the application does not automatically
load `.env` files. Never commit a real key or embed one in an installer.
The language and voice variables are optional. Choose a supported voice that
matches the language you want spoken.

Click the orb once, say the configured local wake word, then give a command.
Recognition uses one utterance per wake cycle. An unrecognized utterance returns
an empty command. Service failures raise actionable errors; Azure mode never
silently switches to another cloud recognition provider.

To restore the previous provider:

```powershell
$env:NEXUS_SPEECH_PROVIDER = "default"
```

## Verification

```powershell
python -m unittest discover -s tests -v
```

Tests mock SDK responses and require no Azure account or microphone. For a live
smoke test, verify a spoken response and a simple command such as "open YouTube",
then say the wake word and "stop". Test invalid credentials and loss of network
before publishing a release. Live service/audio verification is separate from
the mocked tests.

## Contribution path

Using this SDK does not grant a Microsoft badge or make this an official
Microsoft sample. A focused sample or fix can be proposed to upstream maintainers;
acceptance and any recognition are separate decisions.

- [Microsoft speech-to-text quickstart](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-speech-to-text)
- [Microsoft text-to-speech quickstart](https://learn.microsoft.com/azure/ai-services/speech-service/get-started-text-to-speech)
- [Speech SDK samples](https://github.com/Azure-Samples/cognitive-services-speech-sdk)

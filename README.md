# NEXUS — AI Desktop Assistant

[![Tests](https://github.com/AyushPal0/NEXUS/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/AyushPal0/NEXUS/actions/workflows/tests.yml)

NEXUS is an AI-powered desktop assistant that can control your computer using voice commands.

## Features

- Voice commands
- Wake word activation (Hey Nexus)
- Desktop automation
- Floating assistant UI
- Screen vision AI
- Memory system
- Multi-step task execution
- System tray mode
- Startup with Windows

## Tech Stack

Python  
PyQt6  
SpeechRecognition  
Vosk  
Ollama (Local LLM)  
OpenCV  
PyAutoGUI  

## Example Commands

Hey Nexus open chrome  
Hey Nexus take a screenshot  
Hey Nexus create a folder called project  

## Project Structure
backend/
frontend/
assets/
run_nexus.py


## Future Improvements

- Web search integration
- AI task planning
- Cross-platform support

## Microsoft Azure Speech (optional)

See [setup and verification](docs/azure-speech.md) to use Microsoft Speech SDK
for voice commands and responses while retaining the existing UI and wake word.

## Automated tests

GitHub Actions runs the regression and offscreen Qt interface tests on Windows
with Python 3.11 and 3.13 for pushes and pull requests. The workflow can also be
started manually from the Actions tab.

To run the same suite locally, use a dedicated test environment:

```powershell
python -m venv .venv-tests
.\.venv-tests\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv-tests\Scripts\python.exe -m unittest discover -s tests -v
```

The test dependencies include Qt so interface tests are exercised. Speech
services, microphones, desktop actions, and Ollama are mocked; the suite needs
no Azure credentials or downloaded models. Live speech and full application
installation checks are separate from these automated tests.

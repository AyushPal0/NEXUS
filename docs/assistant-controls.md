# Assistant states and stopping

Click the orb to start one assistant session. The status displays Starting,
Waiting for wake word, Listening, Thinking, and Speaking as work progresses.

Use **Stop** to cancel the session. The UI shows Stopping until worker cleanup
finishes, then Idle. A second orb click cannot start another session during
cleanup. Closing the window also requests stop.

- The local Vosk microphone loop checks cancellation while waiting for audio.
- Default speech capture checks cancellation between audio chunks and during
  short silence timeouts; leaving the capture context closes the microphone.
- Azure recognition uses continuous recognition for a cancellable single phrase
  and waits for SDK stop cleanup before allowing another session.
- Default and Azure speech playback receive the same stop signal.
- Stop skips remaining planned actions. An already executing action or network
  request must finish before the worker exits; stopping is cooperative, not an
  interruption of arbitrary Python or SDK code. Google recognition uses a
  network timeout. SDK startup/cleanup and Ollama requests can take longer.

Errors remain visible instead of leaving the UI stuck on Listening. Check the
speech provider's configuration, microphone access, network, Ollama, and local
Vosk model when prompted. Click the orb to retry after correcting setup.
Raw service exceptions are not displayed because they can contain private data.

## Verification

```powershell
python -m unittest discover -s tests -v
```

The session and audio tests use fake devices and services. When PyQt6 is
installed, offscreen Qt tests also check actual button clicks, queued state/error
signals, duplicate starts, retry, and closing the window. Live microphone,
speaker, and Azure account checks remain separate.

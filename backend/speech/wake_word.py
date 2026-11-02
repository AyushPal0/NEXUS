import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer


model = None

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def listen_for_wake_word(stop_event=None):
    global model
    if stop_event is not None and stop_event.is_set():
        return False
    if model is None:
        model = Model("models/vosk-model-small-en-us-0.15")
    # Discard audio left over from the previous session.
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break

    recognizer = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):

        print("Waiting for wake word...")

        while stop_event is None or not stop_event.is_set():

            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(data):

                result = json.loads(recognizer.Result())

                text = result.get("text", "")

                print("Heard:", text)

                if "hey nexus" in text:
                    return True
    return False

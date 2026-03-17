import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer


model = Model("models/vosk-model-small-en-us-0.15")

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def listen_for_wake_word():

    recognizer = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):

        print("Waiting for wake word...")

        while True:

            data = q.get()

            if recognizer.AcceptWaveform(data):

                result = json.loads(recognizer.Result())

                text = result.get("text", "")

                print("Heard:", text)

                if "hey nexus" in text:
                    return True
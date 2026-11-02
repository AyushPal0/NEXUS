"""Capture a single phrase in chunks, releasing the microphone on stop."""


def listen(recognizer, sr, stop_event):
    if stop_event.is_set():
        return ""
    chunks = []
    recognizer.operation_timeout = 10
    with sr.Microphone() as source:
        while not stop_event.is_set():
            try:
                for chunk in recognizer.listen(
                    source, timeout=0.5, phrase_time_limit=15, stream=True
                ):
                    if stop_event.is_set():
                        return ""
                    chunks.append(chunk.frame_data)
                break
            except sr.WaitTimeoutError:
                chunks.clear()
        rate, width = source.SAMPLE_RATE, source.SAMPLE_WIDTH
    if stop_event.is_set() or not chunks:
        return ""
    audio = sr.AudioData(b"".join(chunks), rate, width)
    try:
        result = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    # Network and device errors intentionally reach the visible error handler.
    return "" if stop_event.is_set() else result.lower()

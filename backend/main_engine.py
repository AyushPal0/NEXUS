from backend.speech.speech_engine import listen, speak
from backend.speech.wake_word import listen_for_wake_word
from backend.brain.command_handler import handle_command


def start_nexus():

    speak("Nexus is online")

    while True:

        # wait for wake word
        listen_for_wake_word()

        speak("Yes?")

        command = listen()

        running = handle_command(command, speak)

        if not running:
            break
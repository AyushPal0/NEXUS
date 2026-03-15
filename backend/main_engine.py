from backend.speech.speech_engine import listen, speak
from backend.brain.command_handler import handle_command

def start_nexus():

    speak("Initializing Nexus")

    running = True

    while running:

        command = listen()

        if command:
            running = handle_command(command, speak)
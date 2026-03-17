from backend.brain.ai_brain import ask_ai
from backend.automation.system_control import *
from backend.automation.file_manager import *
from backend.automation.screenshot import *
from backend.automation.camera import *
from backend.brain.screen_vision import analyze_screen

def handle_command(command, speak):

    intent = ask_ai(command)

    print("AI Intent:", intent)

    if "open_chrome" in intent:
        speak("Opening Chrome")
        open_chrome()

    elif "open_youtube" in intent:
        speak("Opening YouTube")
        open_youtube()

    elif "create_folder" in intent:
        speak("Creating folder")
        create_folder()

    elif "take_screenshot" in intent:
        speak("Taking screenshot")
        take_screenshot()

    elif "take_photo" in intent:
        speak("Capturing photo")
        take_photo()

    elif "screen" in intent or "what is on my screen" in command:
        speak("Analyzing your screen")
        result = analyze_screen()
        print(result)
        speak(result)

    elif "stop" in intent:
        speak("Shutting down Nexus")
        return False

    

    else:
        speak("I am not sure how to do that yet")

    return True
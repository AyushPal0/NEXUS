from backend.automation.system_control import *
from backend.automation.file_manager import *
from backend.automation.screenshot import *
from backend.automation.camera import *

def handle_command(command, speak):

    if "open chrome" in command:
        speak("Opening Chrome")
        open_chrome()

    elif "open youtube" in command:
        speak("Opening YouTube")
        open_youtube()

    elif "create folder" in command:
        speak("Creating folder")
        create_folder()

    elif "screenshot" in command:
        speak("Taking screenshot")
        take_screenshot()

    elif "take photo" in command:
        speak("Capturing photo")
        take_photo()

    elif "stop nexus" in command:
        speak("Shutting down")
        return False

    return True
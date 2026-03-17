from backend.brain.ai_brain import ask_ai
from backend.brain.task_agent import plan_tasks
from backend.automation.system_control import *
from backend.automation.file_manager import *
from backend.automation.screenshot import *
from backend.automation.camera import *
from backend.brain.screen_vision import analyze_screen
from backend.utils.memory_manager import remember, recall


def handle_command(command, speak):

    command = command.lower()

    # 🧠 MEMORY: Remember
    if "remember" in command:

        parts = command.replace("remember", "").split("is")

        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()

            remember(key, value)
            speak("Okay, I will remember that.")

        return True

    # 🧠 MEMORY: Recall
    elif command.startswith("what is") or "recall" in command:

        key = command.replace("what is", "").strip()

        value = recall(key)

        if value:
            speak(f"{key} is {value}")
        else:
            speak("I don't remember that.")

        return True

    # 🤖 MULTI-STEP TASK AGENT
    tasks = plan_tasks(command)

    if tasks:
        speak("Executing your request")

        for task in tasks:

            print("Task:", task)

            if "open_chrome" in task:
                open_chrome()

            elif "open_youtube" in task:
                open_youtube()

            elif "create_folder" in task:
                create_folder()

            elif "take_screenshot" in task:
                take_screenshot()

            elif "take_photo" in task:
                take_photo()

        return True

    # 🤖 AI INTENT (Fallback)
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
def parse_intent(command):

    command = command.lower()

    if "chrome" in command:
        return ("open_chrome", None)

    elif "youtube" in command:
        return ("open_youtube", None)

    elif "screenshot" in command:
        return ("take_screenshot", None)

    elif "photo" in command:
        return ("take_photo", None)

    elif "create folder" in command:

        words = command.split()
        name = "NewFolder"

        if "called" in words:
            name = words[words.index("called") + 1]

        return ("create_folder", name)

    elif "stop" in command:
        return ("stop", None)

    return ("unknown", None)
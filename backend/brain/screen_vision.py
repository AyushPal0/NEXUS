import pyautogui
import ollama


def capture_screen():

    screenshot = pyautogui.screenshot()
    path = "screen.png"

    screenshot.save(path)

    return path


def analyze_screen():

    image_path = capture_screen()

    response = ollama.chat(
        model="llava",
        messages=[
            {
                "role": "user",
                "content": "Describe what is happening on this computer screen.",
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]
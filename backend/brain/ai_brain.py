import ollama

def ask_ai(command):

    prompt = f"""
You are an AI assistant controlling a computer.

Convert the user's request into a simple command.

Available commands:

open_chrome
open_youtube
take_screenshot
take_photo
create_folder
stop

User request: {command}

Return ONLY the command.
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"].strip()
import ollama


def plan_tasks(command):

    prompt = f"""
You control a computer assistant.

Break the user request into simple commands.

Available commands:
open_chrome
open_youtube
take_screenshot
take_photo
create_folder

Return commands as a list.

User request: {command}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response["message"]["content"]

    tasks = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            tasks.append(line)

    return tasks
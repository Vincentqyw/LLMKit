import requests

import os
import openai

def analyze_source_code(repo_structure, chatbot, top_p=1.0, temperature=1.0):
    systemPromptTxt = "Serve me as a programming assistant."
    import time

    print("begin analysis on:", repo_structure)
    for index, (file_name, file_content) in enumerate(repo_structure.items()):
        if index == 0:
            prefix = "Next, please analyze the following project files one by one"

        i_say =prefix + f"Please give an overview of the following program file with the file name {file_name} and the file code as ```{file_content}```"

        print(i_say)
        out = chatbot.chat(i_say)
        print(out)

def fetch_directory_contents(base_url, path=""):
    response = requests.get(f"{base_url}/{path}")

    if response.status_code != 200:
        print(f"Error fetching directory contents: {response.status_code}")
        return

    contents = response.json()

    repo_structure = {}
    for content in contents:
        if content["type"] == "file":
            # Fetch file content
            file_response = requests.get(content["download_url"])
            if file_response.status_code != 200:
                print(f"Error fetching file {content['path']}: {file_response.status_code}")
                continue

            file_contents = file_response.text
            repo_structure[content["path"]] = file_contents
        elif content["type"] == "dir":
            # Recursively fetch directory contents
            subdir_structure = fetch_directory_contents(base_url, content["path"])
            repo_structure.update(subdir_structure)

    return repo_structure


class ChatApp:
    def __init__(self, api_key):
        # Set the API key to use the OpenAI API
        openai.api_key = api_key

        # Initialize the messages list with a system message
        self.messages = [
            {
                "role": "system",
                "content": "You are a coding tutor bot to help user summary, write and optimize python code.",
            },
        ]

    def chat(self, message):
        # Add the user's message to the messages list
        self.messages.append({"role": "user", "content": message})

        # Call the OpenAI API with the current messages to get a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )

        # Extract the assistant's message from the response and add it to the messages list
        assistant_message = response["choices"][0]["message"]
        self.messages.append(
            {"role": "system", "content": assistant_message.content}
        )

        # Return the assistant's message
        return assistant_message

def fetch_github_repo_contents(user, repo):
    base_url = f"https://api.github.com/repos/{user}/{repo}/contents"
    return fetch_directory_contents(base_url)


# Replace "user" and "repo" with the desired GitHub user and repository names

API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize the ChatApp instance with the API key
chat_app = ChatApp(API_KEY)

user = "tensorboy"
repo = "LLMKit"
repo_structure = fetch_github_repo_contents(user, repo)

# Print the repository structure
for filename, content in repo_structure.items():
    print(f"File: {filename}\nContent:\n{content}\n")

analyze_source_code(repo_structure, chat_app)
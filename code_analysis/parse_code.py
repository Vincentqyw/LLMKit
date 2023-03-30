import requests

import os
import openai
import gradio as gr
from urllib.parse import urlparse


def parse_github_link(github_link):
    parsed_url = urlparse(github_link)

    # Check if the link is a valid GitHub link
    if parsed_url.netloc != "github.com":
        return None

    path_parts = parsed_url.path.strip("/").split("/")

    # A valid GitHub link should have at least a username and a repository
    if len(path_parts) < 2:
        return None

    username, repo_name = path_parts[:2]
    return username, repo_name


def analyze_source_code(
    repo_structure, chatbot, top_p=1.0, temperature=1.0, file_number=5
):
    systemPromptTxt = "Serve me as a programming assistant."
    import time

    messages = [
        {
            "role": "system",
            "content": "You are a coding tutor bot to help user summary, write and optimize python code.",
        },
    ]
    print("begin analysis on:", repo_structure)
    for index, (file_name, file_content) in enumerate(repo_structure.items()):
        if index > file_number:
            break
        if index == 0:
            prefix = "Next, please analyze the following project files one by one"

        i_say = (
            prefix
            + f"Please give an overview of the following program file with the file name {file_name} and the file code as ```{file_content}```"
        )

        user_message = {"role": "user", "content": i_say}
        messages.append(user_message)
        llm_output = chatbot.single_chat(messages)
        messages.pop(-1)
        single_context = {"role": "system", "content": llm_output.content}
        messages.append(single_context)
        print(llm_output.content)
    all_file = ", ".join(
        [file_name for file_name, file_content in repo_structure.items()][:file_number]
    )
    summary_prompt = f"According to your own analysis, summarize the overall function and structure of the program. Then use a markdown table to organize the functions of each file.（include {all_file}）。"

    user_message = {"role": "user", "content": summary_prompt}
    messages.append(user_message)
    summary_output = chatbot.single_chat(messages)
    print(summary_output.content)
    return summary_output.content


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
                print(
                    f"Error fetching file {content['path']}: {file_response.status_code}"
                )
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

    def single_chat(self, messages):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        assistant_message = response["choices"][0]["message"]
        return assistant_message

    def chat(self, message):
        # Add the user's message to the messages list
        self.messages.append({"role": "user", "content": message})

        # Call the OpenAI API with the current messages to get a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )

        # Extract the assistant's message from the response and add it to the messages list
        assistant_message = response["choices"][0]["message"]
        self.messages.append({"role": "system", "content": assistant_message.content})

        # Return the assistant's message
        return assistant_message


def generate_repo_summary(github_link):
    repo_structure = fetch_github_repo_contents(github_link)
    summary_of_code = analyze_source_code(repo_structure, chat_app)
    return summary_of_code


def fetch_github_repo_contents(github_link):
    username, repo_name = parse_github_link(github_link)
    print(f"Username: {username}\nRepository Name: {repo_name}")
    base_url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
    return fetch_directory_contents(base_url)


API_KEY = os.environ.get("OPENAI_API_KEY")
chat_app = ChatApp(API_KEY)

user = "tensorboy"
repo = "LLMKit"

# Create the Gradio interface
input_repo = gr.Textbox(lines=1, label="Enter Github Link:")
output_table = gr.Textbox(lines=15, label="Summary of Code:")


iface = gr.Interface(
    fn=generate_repo_summary,
    inputs=input_repo,
    outputs=output_table,
    title="GitHub Repository Analyzer",
    description="Summary A Github Repo.",
)

# Launch the Gradio interface
iface.launch(share=True)
# Replace "user" and "repo" with the desired GitHub user and repository names


# Initialize the ChatApp instance with the API key


# Print the repository structure
# for filename, content in repo_structure.items():
#    print(f"File: {filename}\nContent:\n{content}\n")

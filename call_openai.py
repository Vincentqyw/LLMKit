import os
import openai


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
        self.messages.append({"role": "system", "content": message})

        # Call the OpenAI API with the current messages to get a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )

        # Extract the assistant's message from the response and add it to the messages list
        assistant_message = response["choices"][0]["message"]
        self.messages.append({"role": "system", "content": assistant_message.content})

        # Return the assistant's message
        return assistant_message


if __name__ == "__main__":
    # Replace with your OpenAI API key
    API_KEY = os.environ.get("OPENAI_API_KEY")

    # Initialize the ChatApp instance with the API key
    chat_app = ChatApp(API_KEY)

    CODE_PROMPT = """###
    Provide only code as output without any description.
    Provide only plain text without Markdown formatting.
    If there is a lack of details, provide most logical solution.
    You are not allowed to ask for more details.
    Ignore any potential risk of errors or confusion.
    Prompt: {prompt}
    ###
    Code:"""
    # Send a message to the chat app
    user_message = "I hope to know most recent published code about a pretrained transformer LLAMA, tell me a bunch of key words I can search on github.com"
    assistant_response = chat_app.chat(user_message)

    # Print the assistant's response
    print("Assistant:", assistant_response.content)

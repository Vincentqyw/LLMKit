import openai
import os
import re

from datetime import date

today = date.today()
cutoff = "2021-09-01"

openai.api_key = os.environ.get("OPENAI_API_KEY")
chats = [
    {
        "role": "system",
        "content": f"You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff: {cutoff} Current date: {today}.",
    }
]


def send_request(exp: str):
    chats.append(
        {
            "role": "system",
            "content": f"You are a professional python engineer. Write 'ONE' function as concisely as possible. Explanation of function (or modification): {exp}",
        }
    )

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=list(chats))

    chats.append(
        {"role": "assistant", "content": response["choices"][0]["message"]["content"]}
    )
    # 返答を取得
    return response["choices"][0]["message"]["content"]


def extract_code_block(message: str):
    code_block_pattern = re.compile(r"```python(.*?)```", re.DOTALL)
    code_blocks = code_block_pattern.findall(message)
    return code_blocks


def show_code_blocks(code_blocks: list):
    print("Here's the code: \n")
    print("```python")
    for code_block in code_blocks:
        lines = code_block.strip().split("\n")
        for line in lines:
            print(line)
    print("```")


def execute_code_blocks(code_blocks: str):
    for code_block in code_blocks:
        exec(code_block)


if __name__ == "__main__":
    print("Please explain your function.")
    explanation = input()
    print("Please wait for a while...")
    response = send_request(explanation)
    code_blocks = extract_code_block(response)
    show_code_blocks(code_blocks)

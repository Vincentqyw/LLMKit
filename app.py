import gradio as gr
import requests
import pandas as pd
import markdown, mdtex2html, threading
from show_math import convert as convert_math


def text_divide_paragraph(text):
    """
    将文本按照段落分隔符分割开，生成带有段落标签的HTML代码。
    """
    if "```" in text:
        # careful input
        return text
    else:
        # wtf input
        lines = text.split("\n")
        for i, line in enumerate(lines):
            lines[i] = "<p>" + lines[i].replace(" ", "&nbsp;") + "</p>"
        text = "\n".join(lines)
        return text


def markdown_convertion(txt):
    """
    将Markdown格式的文本转换为HTML格式。如果包含数学公式，则先将公式转换为HTML格式。
    """
    if ("$" in txt) and ("```" not in txt):
        return (
            markdown.markdown(txt, extensions=["fenced_code", "tables"])
            + "<br><br>"
            + markdown.markdown(
                convert_math(txt, splitParagraphs=False),
                extensions=["fenced_code", "tables"],
            )
        )
    else:
        return markdown.markdown(txt, extensions=["fenced_code", "tables"])


def format_io(y):
    """
    将输入和输出解析为HTML格式。将y中最后一项的输入部分段落化，并将输出部分的Markdown和数学公式转换为HTML格式。
    """
    if y is None or y == []:
        return []
    i_ask, gpt_reply = y[-1]
    i_ask = text_divide_paragraph(i_ask)
    y[-1] = (
        None
        if i_ask is None
        else markdown.markdown(i_ask, extensions=["fenced_code", "tables"]),
        None if gpt_reply is None else markdown_convertion(gpt_reply),
    )
    return y


def get_github_repos(query):
    headers = {"Accept": "application/vnd.github+json"}
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 50,
    }

    GITHUB_API_URL = "https://api.github.com/search/repositories"
    response = requests.get(GITHUB_API_URL, headers=headers, params=params)

    response_json = response.json()
    print(response_json)

    if "items" in response_json:
        repos = response_json["items"]
        repo_list = [
            {
                "Name": repo["name"],
                "Stars": repo["stargazers_count"],
                "URL": repo["html_url"],
                "Description": repo["description"],
            }
            for repo in repos
        ]
        return pd.DataFrame(repo_list)
    else:
        return pd.DataFrame()


def search_github(query):
    keywords = query.split()
    search_query = " ".join(f"{keyword}" for keyword in keywords)
    repos = get_github_repos(search_query)
    return repos


if __name__ == "__main__":
    input_box = gr.Textbox(lines=1, label="Enter search query:")
    output_table = gr.Dataframe(label="Relevant GitHub Repositories")

    iface = gr.Interface(
        fn=search_github,
        inputs=input_box,
        outputs=output_table,
        title="GitHub Repository Search",
        description="Search for GitHub repositories based on keywords.",
    )

    iface.launch(share=True)
    # Create the Gradio interface
    input_box = gr.Textbox(lines=1, label="Enter search query:")
    output_table = gr.Dataframe(label="Relevant GitHub Repositories")

    iface = gr.Interface(
        fn=search_github,
        inputs=input_box,
        outputs=output_table,
        title="GitHub Repository Search",
        description="Search for GitHub repositories based on keywords.",
    )

    # Launch the Gradio interface
    iface.launch(share=True)

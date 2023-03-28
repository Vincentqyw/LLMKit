import gradio as gr
import requests
import pandas as pd

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

import gradio as gr
import requests

# Replace YOUR_GITHUB_TOKEN with your personal access token
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
GITHUB_API_URL = "https://api.github.com/search/repositories"


def get_github_repos(query):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 5,
    }

    response = requests.get(GITHUB_API_URL, headers=headers, params=params)
    response_json = response.json()

    if "items" in response_json:
        repos = response_json["items"]
        repo_list = [
            {
                "Name": repo["name"],
                "Description": repo["description"],
                "Stars": repo["stargazers_count"],
                "URL": repo["html_url"],
            }
            for repo in repos
        ]
        return repo_list
    else:
        return []


def search_github(query):
    keywords = query.split()
    search_query = " ".join(f"{keyword}" for keyword in keywords)
    repos = get_github_repos(search_query)
    return repos


# Create the Gradio interface
input_box = gr.inputs.Textbox(lines=1, label="Enter search query:")
output_table = gr.outputs.Table(label="Relevant GitHub Repositories")

iface = gr.Interface(
    fn=search_github,
    inputs=input_box,
    outputs=output_table,
    title="GitHub Repository Search",
    description="Search for GitHub repositories based on keywords.",
)

# Launch the Gradio interface
iface.launch()

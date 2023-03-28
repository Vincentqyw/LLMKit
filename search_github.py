import requests
def search_github_repos(query, sort='updated', order='desc', per_page=10):
    url = "https://api.github.com/search/repositories"
    headers = {'Accept': 'application/vnd.github+json'}
    params = {
        'q': query,
        'sort': sort,
        'order': order,
        'per_page': per_page
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data from GitHub (Status Code: {response.status_code})")
        return None

if __name__ == "__main__":
    query = "machine learning"
    results = search_github_repos(query)

    if results:
        for repo in results['items']:
            print(f"Repository Name: {repo['name']}")
            print(f"URL: {repo['html_url']}")
            print(f"Stars: {repo['stargazers_count']}")
            print(f"Forks: {repo['forks_count']}")
            print(f"Updated at: {repo['updated_at']}")
            print(f"Description: {repo['description']}\n")


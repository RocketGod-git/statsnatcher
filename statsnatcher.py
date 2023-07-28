import requests
import os
import json

# Load configuration from config.json
with open('config.json') as f:
    config = json.load(f)

# Get configuration values
GH_TOKEN = config['GH_TOKEN']
GH_USERNAME = config['GH_USERNAME']

# Base URL for the GitHub API
GH_API_BASE_URL = 'https://api.github.com'

def get_repos():
    """
    Fetches the list of repositories for the configured user
    """
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    repos_url = f'{GH_API_BASE_URL}/users/{GH_USERNAME}/repos'
    response = requests.get(repos_url, headers=headers)
    if response.status_code != 200:
        print(f'Error fetching repositories: {response.status_code}, {response.text}')
        return []

    repos_data = response.json()
    return [repo['name'] for repo in repos_data]

def get_repo_info(repo):
    """
    Fetches the repository's star count, fork count, clone count, referral paths, referral sources, and page views
    """
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get repo details
    repo_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}'
    repo_response = requests.get(repo_url, headers=headers)
    if repo_response.status_code != 200:
        print(f'Error fetching repository details for {repo}: {repo_response.status_code}, {repo_response.text}')
        return None

    repo_data = repo_response.json()

    # Get repo clone count
    clone_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/clones'
    clone_response = requests.get(clone_url, headers=headers)
    clone_data = clone_response.json()

    # Get repo referral paths
    referral_path_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/popular/paths'
    referral_path_response = requests.get(referral_path_url, headers=headers)
    referral_path_data = referral_path_response.json()

    # Get repo referral sources
    referral_source_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/popular/referrers'
    referral_source_response = requests.get(referral_source_url, headers=headers)
    referral_source_data = referral_source_response.json()

    # Get repo page views
    page_views_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/views'
    page_views_response = requests.get(page_views_url, headers=headers)
    page_views_data = page_views_response.json()

    # Return a dictionary with the necessary details
    return {
        'name': repo,
        'stars': repo_data['stargazers_count'],
        'forks': repo_data['forks'],
        'clones': clone_data['count'],
        'referral_paths': referral_path_data,
        'referral_sources': referral_source_data,
        'page_views': page_views_data['count']
    }

def update_readme(repos):
    """
    Updates the README with the given repository stats
    """
    # Generate markdown for each repo
    star_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - ★ {repo["stars"]}' for repo in repos])
    fork_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 🍴 {repo["forks"]}' for repo in repos])
    clone_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 🔄 {repo["clones"]}' for repo in repos])
    page_view_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 👁️‍🗨️ {repo["page_views"]}' for repo in repos])

    # Generate referral path list
    referral_path_list = '\n'.join([f'1. [{path["title"]}](https://github.com{path["path"]}) - 👣 {path["count"]}' for repo in repos for path in repo['referral_paths']])

    # Generate referral source list
    referral_source_list = '\n'.join([f'1. {source["referrer"]} - 🌍 {source["count"]}' for repo in repos for source in repo['referral_sources']])

    # Read the README template
    with open('README_template.md', 'r') as f:
        readme = f.read()

    # Update the README
    new_readme = readme.replace('<!-- STAR_LIST -->', star_list).replace('<!-- FORK_LIST -->', fork_list).replace('<!-- CLONE_LIST -->', clone_list).replace('<!-- PAGE_VIEW_LIST -->', page_view_list).replace('<!-- REFERRAL_PATH_LIST -->', referral_path_list).replace('<!-- REFERRAL_SOURCE_LIST -->', referral_source_list)
    with open('README.md', 'w') as f:
        f.write(new_readme)

def main():
    print('Fetching list of repositories...')
    repos = get_repos()
    print(f'Fetched {len(repos)} repositories.')

    print('Fetching repository information...')
    repo_info = [get_repo_info(repo) for repo in repos if repo is not None]
    print('Finished fetching repository information.')

    print('Sorting repository information...')
    repo_info.sort(key=lambda r: r['stars'], reverse=True)
    print('Finished sorting repository information.')

    print('Updating README...')
    update_readme(repo_info)
    print('Finished updating README.')

if __name__ == '__main__':
    main()
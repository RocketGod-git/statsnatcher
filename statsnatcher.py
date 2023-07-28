# __________                  __             __     ________             .___ 
# \______   \  ____    ____  |  | __  ____ _/  |_  /  _____/   ____    __| _/ 
#  |       _/ /  _ \ _/ ___\ |  |/ /_/ __ \\   __\/   \  ___  /  _ \  / __ |  
#  |    |   \(  <_> )\  \___ |    < \  ___/ |  |  \    \_\  \(  <_> )/ /_/ |  
#  |____|_  / \____/  \___  >|__|_ \ \___  >|__|   \______  / \____/ \____ |  
#         \/              \/      \/     \/               \/              \/  
#
import requests
import os
import json
from git import Repo
import time

def countdown(t):
    while t:
        hrs, remainder = divmod(t, 3600)
        mins, secs = divmod(remainder, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hrs, mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

# Load configuration from config.json
with open('config.json') as f:
    config = json.load(f)

# Get configuration values
GH_TOKEN = config['GH_TOKEN']
GH_USERNAME = config['GH_USERNAME']
LOCAL_REPO_PATH = config['LOCAL_REPO_PATH']
BRANCH_NAME = config['BRANCH_NAME']

# Base URL for the GitHub API
GH_API_BASE_URL = 'https://api.github.com'
REPO_URL = f"https://github.com/{GH_USERNAME}/{GH_USERNAME}.git"  # Define the repository URL here

def get_repos():
    """
    Fetches the list of repositories for the configured user
    """
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    repos_url = f'{GH_API_BASE_URL}/users/{GH_USERNAME}/repos'
    all_repos = []
    while repos_url:
        response = requests.get(repos_url, headers=headers)
        if response.status_code != 200:
            print(f'Error fetching repositories: {response.status_code}, {response.text}')
            return []

        repos_data = response.json()
        all_repos += [repo['name'] for repo in repos_data if not repo['fork']]

        # Check if there are more pages of repositories
        link_header = response.headers.get('Link')
        if link_header:
            # Extract the URL for the next page, if it exists
            links = link_header.split(', ')
            repos_url = None
            for link in links:
                url, rel = link.split('; ')
                if rel == 'rel="next"':
                    # Remove < and > around the URL
                    repos_url = url[1:-1]
                    break
        else:
            break

    return all_repos

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
    # Sort repos by stars, forks, clones, and page views
    sorted_by_stars = sorted(repos, key=lambda repo: repo['stars'], reverse=True)
    sorted_by_forks = sorted(repos, key=lambda repo: repo['forks'], reverse=True)
    sorted_by_clones = sorted(repos, key=lambda repo: repo['clones'], reverse=True)
    sorted_by_page_views = sorted(repos, key=lambda repo: repo['page_views'], reverse=True)

    # Generate markdown for each repo
    star_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - ★ {repo["stars"]}' for repo in sorted_by_stars])
    fork_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 🍴 {repo["forks"]}' for repo in sorted_by_forks])
    clone_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 🔄 {repo["clones"]}' for repo in sorted_by_clones])
    page_view_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - 👁️‍🗨️ {repo["page_views"]}' for repo in sorted_by_page_views])

    # Generate referral path list
    referral_path_list = '\n'.join([f'1. [{path["title"]}](https://github.com{path["path"]}) - 👣 {path["count"]}' for repo in repos for path in repo['referral_paths']])

    # Generate referral source list
    referral_source_list = '\n'.join([f'1. {source["referrer"]} - 🌍 {source["count"]}' for repo in repos for source in repo['referral_sources']])

    # Read the README template
    with open('README_template.md', 'r') as f:
        readme = f.read()

    # Update the README
    new_readme = readme.replace('<!-- STAR_LIST -->', star_list).replace('<!-- FORK_LIST -->', fork_list).replace('<!-- CLONE_LIST -->', clone_list).replace('<!-- PAGE_VIEW_LIST -->', page_view_list).replace('<!-- REFERRAL_PATH_LIST -->', referral_path_list).replace('<!-- REFERRAL_SOURCE_LIST -->', referral_source_list)
    
    # Define the path to the README in the local repository
    readme_path = os.path.join(LOCAL_REPO_PATH, 'README.md')

    # Write the updated contents to the README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_readme)
    
def commit_and_push_changes(repo):
    """
    Commits the updated README and pushes the changes to GitHub
    """
    # Check if there are any changes
    if repo.is_dirty():
        # Add the updated README to the staging area
        repo.git.add('README.md')

        # Commit the changes
        repo.git.commit('-m', 'Update README with latest stats')

        # Push the changes to GitHub
        repo.git.push('origin', BRANCH_NAME)
    else:
        print('No changes to commit')

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

    print('Opening or cloning GitHub profile repository...')
    if os.path.isdir(LOCAL_REPO_PATH):
        # If the directory already exists, just open the repository
        repo = Repo(LOCAL_REPO_PATH)
    else:
        # Otherwise, clone the repository
        repo = Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    print('Opened or cloned GitHub profile repository.')

    print('Updating README...')
    update_readme(repo_info)
    print('Finished updating README.')

    print('Committing changes and pushing to GitHub...')
    commit_and_push_changes(repo)
    print('Finished committing changes and pushing to GitHub.')

if __name__ == '__main__':
    while True:
        # Run the main function
        main()

        # Countdown to next update
        print('Countdown to next update:')
        countdown(24*60*60) # 24 hours in seconds

        # Wait for 24 hours
        time.sleep(24*60*60)
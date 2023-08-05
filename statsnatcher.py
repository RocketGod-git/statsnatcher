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
import traceback

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

    # Get repo contributors and combine duplicates
    contributors_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/contributors'
    contributors_response = requests.get(contributors_url, headers=headers)
    contributors_data = contributors_response.json()
    combined_contributors = {}
    for contributor in contributors_data:
        if contributor['login'] in combined_contributors:
            combined_contributors[contributor['login']] += contributor['contributions']
        else:
            combined_contributors[contributor['login']] = contributor['contributions']

    # Get repo clone count
    clone_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/clones'
    clone_response = requests.get(clone_url, headers=headers)
    clone_data = clone_response.json()

    # Get repo referral paths
    referral_path_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/popular/paths'
    referral_path_response = requests.get(referral_path_url, headers=headers)
    referral_path_data = referral_path_response.json()

    # Get repo referral sources and combine duplicates
    referral_source_url = f'{GH_API_BASE_URL}/repos/{GH_USERNAME}/{repo}/traffic/popular/referrers'
    referral_source_response = requests.get(referral_source_url, headers=headers)
    referral_source_data = referral_source_response.json()
    combined_referral_sources = {}
    for source in referral_source_data:
        if source['referrer'] in combined_referral_sources:
            combined_referral_sources[source['referrer']] += source['count']
        else:
            combined_referral_sources[source['referrer']] = source['count']

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
        'referral_sources': combined_referral_sources,
        'page_views': page_views_data['count'],
        'contributors': combined_contributors
    }

def generate_stat_list(stat_name, repos):
    """
    Generate a markdown list of repository statistics.
    """
    # Define stat symbols
    symbols = {
        'stars': '★',
        'forks': '🍴',
        'clones': '🔄',
        'page_views': '👁️‍🗨️'
    }

    # Sort repos by stat
    sorted_repos = sorted(repos, key=lambda x: x[stat_name], reverse=True)

    # Generate stat list
    stat_list = '\n'.join([f'1. [{repo["name"]}](https://github.com/{GH_USERNAME}/{repo["name"]}) - {symbols[stat_name]} {repo[stat_name]}' for repo in sorted_repos])

    return stat_list

def update_readme(repos):
    """
    Updates the README with the given repository stats
    """
    # Aggregate contributors, referral paths, and referral sources across repos
    contributors = {}
    referral_paths = {}
    referral_sources = {}
    for repo in repos:
        for contributor, contributions in repo['contributors'].items():
            if contributor in contributors:
                contributors[contributor] += contributions
            else:
                contributors[contributor] = contributions
        for path in repo['referral_paths']:
            if path['path'] in referral_paths:
                referral_paths[path['path']] += path['count']
            else:
                referral_paths[path['path']] = path['count']
        for source, count in repo['referral_sources'].items():
            if source in referral_sources:
                referral_sources[source] += count
            else:
                referral_sources[source] = count

    # Sort contributors, referral paths, and referral sources
    sorted_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
    sorted_referral_paths = sorted(referral_paths.items(), key=lambda x: x[1], reverse=True)
    sorted_referral_sources = sorted(referral_sources.items(), key=lambda x: x[1], reverse=True)

    # Generate markdown for each stat
    star_list = generate_stat_list('stars', repos)
    fork_list = generate_stat_list('forks', repos)
    clone_list = generate_stat_list('clones', repos)
    page_view_list = generate_stat_list('page_views', repos)

    # Generate contributors list
    contributors_list = '\n'.join([f'1. [{contributor}](https://github.com/{contributor}) - 💼 {contributions}' for contributor, contributions in sorted_contributors])

    # Generate referral paths list
    referral_paths_list = '\n'.join([f'1. {path} - 🌍 {count}' for path, count in sorted_referral_paths])

    # Generate referral source list
    referral_source_list = '\n'.join([f'1. {referrer} - 🌍 {count}' for referrer, count in sorted_referral_sources])

    # Read the README template
    with open('README_template.md', 'r') as f:
        readme = f.read()

    # Update the README
    new_readme = readme.replace('<!-- STAR_LIST -->', star_list)
    new_readme = new_readme.replace('<!-- FORK_LIST -->', fork_list)
    new_readme = new_readme.replace('<!-- CLONE_LIST -->', clone_list)
    new_readme = new_readme.replace('<!-- PAGE_VIEW_LIST -->', page_view_list)
    new_readme = new_readme.replace('<!-- CONTRIBUTOR_LIST -->', contributors_list)
    new_readme = new_readme.replace('<!-- REFERRAL_PATH_LIST -->', referral_paths_list)
    new_readme = new_readme.replace('<!-- REFERRAL_SOURCE_LIST -->', referral_source_list)
    new_readme = new_readme.replace('<!-- TIMESTAMP -->', time.strftime("%Y-%m-%d %H:%M:%S"))

    # Define the path to the README in the local repository
    readme_path = os.path.join(LOCAL_REPO_PATH, 'README.md')

    # Write the updated contents to the README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_readme)

def commit_and_push_changes(repo):
    """
    Commits the updated README and pushes the changes to GitHub
    """
    # Add the updated README to the staging area
    repo.git.add('README.md')

    # Commit the changes
    repo.git.commit('-m', 'Update README with latest stats')

    # Push the changes to GitHub
    repo.git.push('origin', BRANCH_NAME)

def main():
    try:
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
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print detailed traceback
        traceback.print_exc()

        # Write the error to a log file
        with open("error_log.txt", "a") as f:
            f.write(f"An error occurred: {str(e)}\n")
            f.write(traceback.format_exc())
            f.write("\n")

if __name__ == '__main__':
    while True:
        # Initialize repo to None
        repo = None

        try:
            # Run the main function
            main()

            # Countdown to next update
            print('Countdown to next update:')
            countdown(24*60*60) # 24 hours in seconds

            # Wait for 24 hours
            time.sleep(24*60*60)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # Print detailed traceback
            traceback.print_exc()

            # Write the error to a log file
            with open("error_log.txt", "a") as f:
                f.write(f"An error occurred: {str(e)}\n")
                f.write(traceback.format_exc())
                f.write("\n")
        
        # Commit changes and push to GitHub
        if repo is not None:
            commit_and_push_changes(repo)

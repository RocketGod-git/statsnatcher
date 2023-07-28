# GitHub Stats Snatcher and automatic readme.md updater

GitHub Stats Snatcher is a powerful and easy-to-use Python script that fetches and updates your GitHub statistics automatically. It fetches repository information such as star count, fork count, clone count, referral paths, referral sources, and page views, and updates your README file with these statistics. This is the perfect tool for individuals who want to keep their GitHub profile up to date with their latest project statistics. It also filters out forks so that only original work will be shown.

## Features

- Fetches repository statistics from the GitHub API
- Updates your README.md file with the latest statistics
- Runs automatically, updating your statistics once every 24 hours
- Allows for customization of your README through a template

## Installation

Follow the steps below to setup GitHub Stats Snatcher on your local system.

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. Clone this repository to your local machine:

```bash
git clone https://github.com/RocketGod-git/statsnatcher.git
```

2. Navigate to the repository's directory:

```bash
cd statsnatcher
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Edit the `config.json` file in the same directory as the script with the following structure:

```json
{
    "GH_TOKEN": "<your GitHub token>",
    "GH_USERNAME": "<your GitHub username>",
    "LOCAL_REPO_PATH": "<path to your local repository>",
    "BRANCH_NAME": "<name of the branch>" #usually main or master
}
```

Replace `<your GitHub token>`, `<your GitHub username>`, `<path to your local repository>`, and `<name of the branch>` with your own details.

5. Customize the `README_template.md` file to suit your profile. This file contains placeholders that the script will replace with the relevant statistics. 

Here is an example of what it could look like:

```markdown
# <Your Name>

Find me on my Discord server [here](<Your Discord Server Link>).

Find me on YouTube [here](<Your YouTube Channel Link>).

<img align="right" width="400" src="https://github-readme-stats.vercel.app/api?username=<Your GitHub Username>&show_icons=true&theme=aura&include_all_commits=true"/>

## My Top Repositories
Sorted by stars, forks, clones, and page views.

### Most Starred
<!-- STAR_LIST -->

### Most Forked
<!-- FORK_LIST -->

### Most Cloned
<!-- CLONE_LIST -->

### Most Viewed
<!-- PAGE_VIEW_LIST -->

## Top Referral Paths
<!-- REFERRAL_PATH_LIST -->

## Top Referral Sources
<!-- REFERRAL_SOURCE_LIST -->

Stats provided by [GitHub Stats Snatcher](https://github.com/RocketGod-git/statsnatcher)
```

Replace `<Your Name>`, `<Your Discord Server Link>`, `<Your YouTube Channel Link>`, and `<Your GitHub Username>` with your own details.

6. Run the script:

```bash
python statsnatcher.py
```

The script will now fetch your repository data, update your README, and push the changes to GitHub. It will then wait for 24 hours before running again.

Enjoy your automatically updated GitHub statistics!

## License

This project is licensed under the GNU License. See the [LICENSE](LICENSE) file for details.

![RocketGod](https://github.com/RocketGod-git/shell-access-discord-bot/assets/57732082/c68635fa-b89d-4f74-a1cb-5b5351c22c98)

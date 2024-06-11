import requests
import json
import csv




GITHUB_API_URL = "https://api.github.com/search/repositories"


topic = "healthcare"
# Define the query parameters
params = {
    "q": f"topic:{topic}",
    "sort": "stars",
    "order": "desc",
    "per_page": 100  
}

# token = "your_personal_access_token"
headers = {
    # 'Authorization': f'token {token}'
}

# Keys to retain when fetching

keys_to_keep = [
    "id", "name", "full_name", "private", "html_url", "description",
    "forks_count", "disabled", "allow_forking", "is_template",
    "topics", "visibility", "forks"
]

owner_keys_to_keep = [
    "login", "id", "avatar_url", "url", "html_url", "organizations_url"
]
license_keys_to_keep = [
    "key", "name", "spdx_id", "url", "node_id"
]

def fetch_repositories():
    response = requests.get(GITHUB_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print(f"Failed to fetch repositories: {response.status_code}")
        return []

def filter_repo_data(repo):
    filtered_repo = {key: repo[key] for key in keys_to_keep if key in repo}
    if 'owner' in repo:
        for key in owner_keys_to_keep:
            filtered_repo[f'owner_{key}'] = repo['owner'].get(key, None)
    if 'license' in repo and repo['license'] is not None:
        for key in license_keys_to_keep:
            filtered_repo[f'license_{key}'] = repo['license'].get(key, None)
    return filtered_repo


def save_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def save_to_csv(data, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for repo in data:
            writer.writerow(repo)

def main():
    repos = fetch_repositories()

    if not repos:
        print("No repositories found.")
        return

    # Filter repository data
    filtered_repos = [filter_repo_data(repo) for repo in repos]
    
    # Save all collected information to JSON
    save_to_json(filtered_repos, './data/fetched_repos_all_info.json')
    
    # Extract URLs and save them to JSON
    urls = [repo['html_url'] for repo in repos]
    save_to_json(urls, './configs/fetched_repos.json')
    
    # Save all collected information to CSV
    save_to_csv(filtered_repos, f'./data/{topic}-opensource-repos.csv')

    print("Data saved to files.")

if __name__ == "__main__":
    main()

from argparse import ArgumentParser, Namespace
import http.client
import json

parser = ArgumentParser()
parser.add_argument('username', type=str, help="GitHub username to fetch activity")
args: Namespace = parser.parse_args()

headers = {
    "User-Agent": "github-fetch.py/1.0"
}

connection = http.client.HTTPSConnection("api.github.com")
connection.request("GET", f"/users/{args.username}/events", headers=headers)
response = connection.getresponse()

if response.status == 200:
    raw_data = response.read()
    data = json.loads(raw_data.decode("utf-8"))
    
    if not isinstance(data, list):
        print("Error: Invalid API response format.")
        exit()

    if not data:
        print("No recent activity found.")
    else:
        for event in data:
            event_type = event.get("type", "UnknownEvent")
            repo_info = event.get("repo", {})
            repo_name = repo_info.get("name", "unknown")

            if event_type == "PushEvent":
                commits = event.get("payload", {}).get("commits", [])
                commit_count = len(commits)
                print(f"- Pushed {commit_count} commits to {repo_name}")

            elif event_type == "IssuesEvent":
                action = event.get("payload", {}).get("action", "modified")
                print(f"- {action.capitalize()} an issue in {repo_name}")

            elif event_type == "WatchEvent":
                print(f"- Starred {repo_name}")

            elif event_type == "ForkEvent":
                print(f"- Forked {repo_name}")

            elif event_type == "CreateEvent":
                ref_type = event.get("payload", {}).get("ref_type", "resource")
                print(f"- Created a new {ref_type} in {repo_name}")

else:
    if response.status == 403:
        print("Error 403: Rate limit exceeded. Add an access token to avoid this.")
    elif response.status == 404:
        print(f"Error 404: User '{args.username}' not found.")
    else:
        print(f"Error: {response.status} - {response.reason}")

connection.close()
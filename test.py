import requests
import os
from dotenv import load_dotenv

# Load only the API token from .env
load_dotenv()
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# 🔒 Still secure: API token stays out of the code
if not JIRA_API_TOKEN:
    raise ValueError("API token not found in .env file!")

# Hardcoded details (based on your example)
JIRA_EMAIL = "ansh.sharma@kimbal.io"  # <-- Replace with your real Atlassian email
JIRA_DOMAIN = "sinhaludyog.atlassian.net"
JIRA_PROJECT_KEY = "SH"

# Authentication
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

# Jira REST API URL
url = f"https://{JIRA_DOMAIN}/rest/api/3/search"

# Pagination setup
max_results = 100
start_at = 0
all_issues = []

while True and start_at<200:
    query = {
        'jql': f'project = {JIRA_PROJECT_KEY}',
        'maxResults': max_results,
        'startAt': start_at,
        'fields': 'key,summary,status'
    }

    response = requests.get(url, params=query, auth=auth)

    if response.status_code != 200:
        print(f"❌ Error fetching issues: {response.status_code}")
        print(response.text)
        break

    data = response.json()
    issues = data.get("issues", [])
    all_issues.extend(issues)

    print(f"Fetched {len(issues)} issues...")

    if start_at + max_results >= data.get("total", 0):
        break

    start_at += max_results

# Save results
with open("jira_tickets_all.txt", "w", encoding="utf-8") as f:
    for issue in all_issues:
        key = issue["key"]
        summary = issue["fields"]["summary"]
        status = issue["fields"]["status"]["name"]
        line = f"{key}: {summary} [{status}]"
        print(line)
        f.write(line + "\n")

print(f"✅ Total issues fetched: {len(all_issues)}")
print("📄 Saved to jira_tickets_all.txt")

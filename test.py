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
headers = {"Accept": "application/json"}
all_issues = []

while True and start_at<200:
    query = {
        'jql': f'project = {JIRA_PROJECT_KEY}',
        'maxResults': max_results,
        'startAt': start_at,
        'fields': 'key'
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
        issue_key = issue["key"]

        # === Fetch full issue details ===
        issue_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"
        issue_response = requests.get(issue_url, headers=headers, auth=auth)
        if issue_response.status_code != 200:
            print(f"Failed to fetch issue {issue_key}")
            continue

        fields = issue_response.json().get("fields", {})
        issue_data = {
            "Key": issue_key,
            "Summary": fields.get("summary"),
            "Project": fields.get("project", {}).get("name"),
            "Assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
            "Description": "No description",
            "Status": fields.get("status", {}).get("name"),
            "Issue Type": fields.get("issuetype", {}).get("name"),
            "Created Date": fields.get("created"),
            "Comments": {}
        }

        # === Parse description ===
        description = fields.get("description")
        if description:
            desc_text = []
            for block in description.get("content", []):
                if block.get("type") == "paragraph":
                    for content in block.get("content", []):
                        if content.get("type") == "text":
                            desc_text.append(content.get("text"))
            issue_data["Description"] = " ".join(desc_text)

        # === Fetch comments ===
        comments_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/comment"
        comments_response = requests.get(comments_url, headers=headers, auth=auth)
        comments_data = comments_response.json().get("comments", [])

        for comment in comments_data:
            author = comment.get("author", {}).get("displayName", "Unknown")
            body = comment.get("body", {}).get("content", [])
            text_parts = []

            for part in body:
                if part.get("type") == "paragraph":
                    for subpart in part.get("content", []):
                        if subpart.get("type") == "text":
                            text_parts.append(subpart.get("text"))

            comment_text = " ".join(text_parts)
            if author not in issue_data["Comments"]:
                issue_data["Comments"][author] = []
            issue_data["Comments"][author].append(comment_text)

        # === Output to console and file ===
        f.write("\n=== Issue Details ===\n")
        print("\n=== Issue Details ===")
        for key, value in issue_data.items():
            if key != "Comments":
                line = f"{key}: {value}"
                print(line)
                f.write(line + "\n")
            else:
                print("Comments:")
                f.write("Comments:\n")
                for author, comments in value.items():
                    author_line = f"  {author}:"
                    print(author_line)
                    f.write(author_line + "\n")
                    for c in comments:
                        comment_line = f"    - {c}"
                        print(comment_line)
                        f.write(comment_line + "\n")

print(f"\n✅ Total issues fetched: {len(all_issues)}")
print("📄 Detailed data saved to jira_tickets_all.txt")


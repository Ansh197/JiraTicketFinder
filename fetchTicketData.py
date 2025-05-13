import requests
import os
from dotenv import load_dotenv
import csv

# Load only the API token from .env
load_dotenv()
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# 🔒 Still secure: API token stays out of the code
if not JIRA_API_TOKEN:
    raise ValueError("API token not found in .env file!")
if not JIRA_EMAIL:
    raise ValueError("Email not found in .env file!")
if not JIRA_DOMAIN:
    raise ValueError("Domain not found in .env file!")
if not JIRA_PROJECT_KEY:
    raise ValueError("Project Key not found in .env file!")

# Authentication
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

# Jira REST API URL
url = f"https://{JIRA_DOMAIN}/rest/api/3/search"

# Pagination setup
max_results = 500
start_at = 0
headers = {"Accept": "application/json"}
all_issues = []

issue_count = 0 

while True :
    query = {
        'jql': f'project = {JIRA_PROJECT_KEY}',
        'maxResults': max_results,
        'startAt': start_at,
        'fields': 'key'
    }

    response = requests.get(url, params=query, auth=auth)

    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}")
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
with open("jira_tickets_all.csv", "w", encoding="utf-8", newline='') as csvfile:
    fieldnames = ["Key", "Summary", "Project", "Assignee", "Description", "Status", "Issue Type", "Created Date", "Comments"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for issue in all_issues:
        issue_key = issue["key"]

        # Fetch issue details
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
            "Comments": ""
        }

        # Removing alerts
        if issue_data['Issue Type'] == 'Alerts':
            continue

        # Parse description
        description = fields.get("description")
        if description:
            desc_text = []
            for block in description.get("content", []):
                if block.get("type") == "paragraph":
                    for content in block.get("content", []):
                        if content.get("type") == "text":
                            desc_text.append(content.get("text"))
            issue_data["Description"] = " ".join(desc_text)

        # Fetch comments
        comments_url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/comment"
        
        # Adding Error Handling

        try:
            comments_response = requests.get(comments_url, headers=headers, auth=auth, timeout=10)
            comments_response.raise_for_status()
            comments_data = comments_response.json().get("comments", [])

        except requests.exceptions.HTTPError as http_err:
            print(f"[HTTP Error] Issue {issue_key} → {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"[Connection Error] Issue {issue_key} → {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"[Timeout] Issue {issue_key} → {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"[Request Exception] Issue {issue_key} → {req_err}")
        except Exception as e:
            print(f"[Unexpected Error] Issue {issue_key} → {e}")

        comment_lines = []
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
            comment_lines.append(f"{author}: {comment_text}")

        issue_data["Comments"] = " | ".join(comment_lines)

        # Write to CSV
        writer.writerow(issue_data)
        issue_count += 1
        print(f"Issue_Count: {issue_count}, IssueKey: {issue_key}")

print(f"\n Total issues saved to jira_tickets_all.csv: {len(all_issues)}")
# Ticket info saved till SH-5772


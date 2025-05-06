import requests
from requests.auth import HTTPBasicAuth
import os

load_dotenv()

# Jira details
jira_domain = "https://sinhaludyog.atlassian.net"
issue_key = "SH-5153"
url = f"{jira_domain}/rest/api/3/issue/{issue_key}"

# Your credentials
email = "ansh.sharma@kimbal.io"  
api_token = os.getenv("ATLASSIAN_API_TOKEN")   

# Make the request
response = requests.get(
    url,
    auth=HTTPBasicAuth(email, api_token),
    headers={"Accept": "application/json"}
)

# Print the result
if response.status_code == 200:
    issue_data = response.json()
    print(issue_data['fields'])
    print(f"Summary: {issue_data['fields']['summary']}")
    print(f"Status: {issue_data['fields']['status']['name']}")
else:
    print(f"Error {response.status_code}: {response.text}")

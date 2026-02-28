import os
import requests
import base64
import json

# Pull the secure keys from GitHub's hidden vault
APP_KEY = os.environ.get("PARTNERIZE_APP_KEY")
USER_API_KEY = os.environ.get("PARTNERIZE_API_KEY")
PUBLISHER_ID = os.environ.get("PARTNERIZE_PUB_ID")

if not all([APP_KEY, USER_API_KEY, PUBLISHER_ID]):
    print("Error: Missing credentials. Make sure your GitHub Secrets are named correctly.")
    exit(1)

# Authenticate
credentials = f"{APP_KEY}:{USER_API_KEY}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Accept": "application/json"
}

# Call the API to list all your available data feeds
url = f"https://api.partnerize.com/user/publisher/{PUBLISHER_ID}/feed"

print("Contacting Partnerize API to check available feeds...\n")

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    
    # Parse the data
    data = response.json()
    
    # Print the data beautifully so you can read it in the GitHub logs
    print(json.dumps(data, indent=4))
    
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
    print(f"Response: {response.text}")

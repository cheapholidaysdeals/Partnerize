import requests
import json
import time

# Just testing Gatwick to see what the server says
origins = ["LGW"]
vowels = ["a", "e", "i", "o", "u"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

print("Running Diagnostic Test...")

for origin in origins:
    print(f"\nChecking routes from {origin}...")
    
    for vowel in vowels:
        # Notice we removed the dates to see if it allows a general search!
        url = f"https://www.easyjet.com/holidays/_api/v1.0/destinations/search?query={vowel}&from={origin}"
        
        try:
            response = requests.get(url, headers=headers)
            
            print(f"Query '{vowel}': HTTP Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                dest_count = len(data.get("destinations", []))
                print(f" -> Success! Found {dest_count} raw items for '{vowel}'")
            else:
                print(f" -> Blocked/Failed. Response text: {response.text[:100]}...")
                
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(2)

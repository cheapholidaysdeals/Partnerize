import requests
import json
import time
import datetime

# 1. Your complete list of UK departure airports
origins = [
    "ABZ", # Aberdeen
    "BHD", # Belfast City
    "BFS", # Belfast International
    "BHX", # Birmingham
    "LDY", # City of Derry
    "EDI", # Edinburgh
    "GLA", # Glasgow
    "INV", # Inverness
    "LBA", # Leeds Bradford
    "LPL", # Liverpool John Lennon
    "LGW", # London Gatwick
    "LTN", # London Luton
    "SEN", # London Southend
    "STN", # London Stansted
    "MAN", # Manchester
    "SOU"  # Southampton
]

# 2. The Vowel Hack: Every destination has at least one of these
vowels = ["a", "e", "i", "o", "u"]

# 3. Dynamically set a date 3 months in the future
# We use a 7-day window (days 90 to 97) to ensure we catch weekly flights
today = datetime.date.today()
start_date = (today + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
end_date = (today + datetime.timedelta(days=97)).strftime("%Y-%m-%d")

# Pretend to be a real web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

master_route_map = {}

print(f"Starting route mapping for dates {start_date} to {end_date}...")

for origin in origins:
    print(f"\nChecking routes from {origin}...")
    valid_destinations = set() # Using a set automatically removes duplicates
    
    for vowel in vowels:
        # The hidden API URL with dynamic origin, dates, and vowels
        url = f"https://www.easyjet.com/holidays/_api/v1.0/destinations/search?query={vowel}&from={origin}&startDate={start_date}&endDate={end_date}&flexibleDays=0"
        
        try:
            response = requests.get(url, headers=headers)
            
            # If the API blocks us or the route is completely invalid, skip it
            if response.status_code != 200:
                continue
                
            data = response.json()
            
            # Dig into the JSON structure to extract destination names
            if "destinations" in data:
                for dest in data["destinations"]:
                    # We only want top-level destinations (Resorts, Regions, Cities), not specific individual hotels
                    if dest.get("type") in ["Resort", "Region", "City"]:
                        valid_destinations.add(dest.get("name"))
                        
        except Exception as e:
            print(f"Error checking {origin} with '{vowel}': {e}")
            
        # IMPORTANT: Sleep for 1 second between API calls so easyJet doesn't block GitHub's IP address
        time.sleep(1)
        
    # Convert the set back to a sorted list and save it to our master map
    # If valid_destinations is empty (e.g., for LDY), it just saves an empty list: []
    master_route_map[origin] = sorted(list(valid_destinations))
    print(f"Found {len(valid_destinations)} unique holiday destinations from {origin}")

# 4. Save to our final JSON file for the website search box
with open("searchbox_routes.json", "w", encoding='utf-8') as outfile:
    json.dump(master_route_map, outfile, indent=4)

print("\nSuccess! Saved to searchbox_routes.json")

import requests
import json
import time

origins = [
    "ABZ", "BHD", "BFS", "BHX", "LDY", "EDI", "GLA", "INV", 
    "LBA", "LPL", "LGW", "LTN", "SEN", "STN", "MAN", "SOU"
]

search_seeds = [
    "alg", "ali", "ams", "ant", "ath", "bal", "bar", "ber", "bod", "bud", 
    "can", "cor", "cre", "cro", "cyp", "dal", "dub", "egy", "far", "fra", 
    "fue", "gen", "gra", "gre", "hur", "ibi", "ice", "ita", "kos", "kra", 
    "lan", "lis", "mad", "maj", "mal", "mar", "men", "mil", "mor", "nap", 
    "net", "nic", "pal", "pap", "par", "pol", "por", "pra", "rey", "rho", 
    "rom", "sev", "sha", "spa", "swi", "ten", "tur", "val", "ven", "zan"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

master_route_map = {}

print("Starting full route mapping...")

for origin in origins:
    print(f"\nChecking routes from {origin}...")
    valid_destinations = set() 
    
    for seed in search_seeds:
        url = f"https://www.easyjet.com/holidays/_api/v1.0/destinations/search?query={seed}&from={origin}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "destinations" in data:
                    for dest in data["destinations"]:
                        if dest.get("type") in ["Resort", "Region", "City", "Country"]:
                            valid_destinations.add(dest.get("name"))
        except Exception as e:
            pass
            
        time.sleep(0.5) 
        
    master_route_map[origin] = sorted(list(valid_destinations))
    print(f" -> Found {len(valid_destinations)} unique holiday destinations from {origin}")

with open("searchbox_routes.json", "w", encoding='utf-8') as outfile:
    json.dump(master_route_map, outfile, indent=4)

print("\nSuccess! Saved to searchbox_routes.json")

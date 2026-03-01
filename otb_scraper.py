import requests
import json
import time

# 1. Your massive list of UK departure airports
airports = [
    "BHD", "BFS", "BHX", "BOH", "BRS", "CWL", "LDY", "DUB", "EMA", 
    "EDI", "EXT", "GLA", "PIK", "INV", "LBA", "LPL", "LCY", "LGW", 
    "LHR", "LTN", "SEN", "STN", "MAN", "NCL", "NQT", "SOU", "MME", "ABZ"
]

# 2. Our trusty seed list
search_seeds = [
    "alg", "ali", "ams", "ant", "ath", "bal", "bar", "ber", "bod", "bud", 
    "can", "cor", "cre", "cro", "cyp", "dal", "dub", "egy", "far", "fra", 
    "fue", "gen", "gra", "gre", "hur", "ibi", "ice", "ita", "kos", "kra", 
    "lan", "lap", "lis", "mad", "maj", "mal", "mar", "men", "mil", "mor", 
    "nap", "net", "nic", "pal", "pap", "par", "pol", "por", "pra", "rey", 
    "rho", "rom", "sev", "sha", "spa", "swi", "ten", "tur", "val", "ven", 
    "zan", "isl", "bay", "cos", "san", "riv", "cit", "tow", "bel", "lon"
]

url = "https://www.onthebeach.co.uk/graphql?operation_name=searchableItemsByName"

# We must tell their server we are sending JSON data
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

otb_destinations = {}

print("Starting On the Beach master route mapping...")

# This is the trimmed-down version of the exact GraphQL query you found!
graphql_query = """
query searchableItemsByName($name: String!, $limit: Int, $types: [SearchableItemEnum!]) {
  searchableItemsByName(name: $name, limit: $limit, types: $types) {
    items {
      ... on DestinationInterface {
        type: __typename
        value: id
        label: name
      }
    }
  }
}
"""

for seed in search_seeds:
    # Build the Payload "Letter"
    payload = {
        "operationName": "searchableItemsByName",
        "variables": {
            "name": seed,
            "limit": 50, # Grab the top 50 matches per seed
            "types": ["COUNTRY", "REGION", "TOWN"] # Intentionally skipping HOTEL
        },
        "query": graphql_query
    }

    try:
        # Notice this is requests.post() instead of requests.get()!
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Dig into the GraphQL JSON structure
            items = data.get("data", {}).get("searchableItemsByName", {}).get("items", [])
            
            if items:
                for item in items:
                    name = item.get("label")
                    code = item.get("value")
                    
                    if name and code:
                        otb_destinations[name] = str(code)
                        
    except Exception as e:
        pass
        
    # Politeness pause
    time.sleep(0.5)

# Sort it alphabetically
otb_destinations = dict(sorted(otb_destinations.items()))
print(f" -> Successfully mapped {len(otb_destinations)} unique OTB destinations!")

# 3. Duplicate the master list for every UK airport
# This ensures your website JavaScript works exactly the same as it did for easyJet!
final_json_structure = {}
for apt in airports:
    final_json_structure[apt] = otb_destinations

# 4. Save to a new JSON file
with open("otb_routes.json", "w", encoding='utf-8') as outfile:
    json.dump(final_json_structure, outfile, indent=4)

print("\nSuccess! Saved to otb_routes.json")

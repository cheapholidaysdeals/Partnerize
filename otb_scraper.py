import requests
import json
import time

airports = [
    "BHD", "BFS", "BHX", "BOH", "BRS", "CWL", "LDY", "DUB", "EMA", 
    "EDI", "EXT", "GLA", "PIK", "INV", "LBA", "LPL", "LCY", "LGW", 
    "LHR", "LTN", "SEN", "STN", "MAN", "NCL", "NQT", "SOU", "MME", "ABZ"
]

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

headers = {
    # Added a full browser string so we look like Google Chrome
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

otb_destinations = {}

print("Starting On the Beach master route mapping...")

# This is the EXACT query you found! No modifications.
graphql_query = """query searchableItemsByName($name: String!, $limit: Int, $types: [SearchableItemEnum!]) {
  searchableItemsByName(name: $name, limit: $limit, types: $types) {
    items {
      ... on Hotel {
        type: __typename
        value: id
        label: name
      }
      ... on DestinationInterface {
        type: __typename
        value: id
        label: name
      }
      __typename
    }
    __typename
  }
}"""

for seed in search_seeds:
    payload = {
        "operationName": "searchableItemsByName",
        "variables": {
            "name": seed,
            "limit": 30, # High enough to grab regions before hotels crowd them out
            "types": ["COUNTRY", "REGION", "HOTEL", "TOWN"] # Exact browser match
        },
        "query": graphql_query
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # This will tell us if we hit a security wall!
        if response.status_code != 200:
            print(f"HTTP Error for seed '{seed}': {response.status_code}")
            time.sleep(2)
            continue

        data = response.json()
        
        # Check if GraphQL itself threw an error
        if "errors" in data:
            print(f"GraphQL Error for seed '{seed}': {data['errors'][0].get('message')}")
            continue

        items = data.get("data", {}).get("searchableItemsByName", {}).get("items", [])
        
        found_count = 0
        for item in items:
            # We filter out the Hotels right here in Python!
            if item.get("type") != "Hotel":
                name = item.get("label")
                code = item.get("value")
                
                if name and code:
                    otb_destinations[name] = str(code)
                    found_count += 1
                    
        print(f"Seed '{seed}' -> Found {found_count} regions/towns.")
            
    except Exception as e:
        print(f"Crash on seed '{seed}': {e}")
        
    # SLOW IT DOWN! (1.5 seconds prevents the security bot from banning us)
    time.sleep(1.5) 

otb_destinations = dict(sorted(otb_destinations.items()))
print(f"\n -> Successfully mapped {len(otb_destinations)} unique OTB destinations!")

final_json_structure = {}
for apt in airports:
    final_json_structure[apt] = otb_destinations

with open("otb_routes.json", "w", encoding='utf-8') as outfile:
    json.dump(final_json_structure, outfile, indent=4)

print("Success! Saved to otb_routes.json")

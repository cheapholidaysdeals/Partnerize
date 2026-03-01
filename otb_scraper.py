import cloudscraper # Using our new anti-bot armor!
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

# Disguise our script as a standard Windows Google Chrome browser
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

otb_destinations = {}

print("Starting On the Beach mapping with Anti-Bot protection...")

# The EXACT unmodified query you found in your browser
graphql_query = """query searchableItemsByName($name: String!, $limit: Int, $types: [SearchableItemEnum!]) {
  searchableItemsByName(name: $name, limit: $limit, types: $types) {
    items {
      ... on Hotel {
        type: __typename
        value: id
        label: name
        address {
          city
          __typename
        }
        locationBasedData {
          locationId
          __typename
        }
        locatedIn {
          id
          availableFrom
          seasonality {
            startDate
            endDate
            __typename
          }
          __typename
        }
      }
      ... on DestinationInterface {
        active
        availableFrom
        type: __typename
        value: id
        label: name
        seasonality {
          startDate
          endDate
          __typename
        }
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
            "limit": 40,
            # We ask for everything (including hotels) so the server trusts us
            "types": ["COUNTRY", "REGION", "HOTEL", "TOWN"] 
        },
        "query": graphql_query
    }

    try:
        response = scraper.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"HTTP Error {response.status_code} on seed '{seed}' - Blocked by security!")
            time.sleep(2)
            continue

        data = response.json()
        items = data.get("data", {}).get("searchableItemsByName", {}).get("items", [])
        
        found_count = 0
        for item in items:
            # We instantly delete the Hotels in Python, keeping only Regions/Towns
            if item.get("type") != "Hotel":
                name = item.get("label")
                code = item.get("value")
                
                if name and code:
                    otb_destinations[name] = str(code)
                    found_count += 1
                    
        print(f"Seed '{seed}' -> Found {found_count} regions/towns.")
            
    except Exception as e:
        print(f"Crash on seed '{seed}': {e}")
        
    time.sleep(1.5)

otb_destinations = dict(sorted(otb_destinations.items()))
print(f"\n -> Successfully mapped {len(otb_destinations)} unique OTB destinations!")

final_json_structure = {}
for apt in airports:
    final_json_structure[apt] = otb_destinations

with open("otb_routes.json", "w", encoding='utf-8') as outfile:
    json.dump(final_json_structure, outfile, indent=4)

print("Success! Saved to otb_routes.json")

import requests
import math
import json

API_KEY = "03638390-ffa9-463e-9782-c94b4073565a"
BASE_URL = "https://v3.openstates.org/bills"

def fetch_privacy_bills():
    all_bills = []

    page = 1
    per_page = 20
    total_pages = 1

    while page <= total_pages:
        params = {
            "q": "privacy",
            "page": page,
            "per_page": per_page
        }
        # Use X-API-KEY header (or ?apikey= in params)
        headers = {
            "X-API-KEY": API_KEY
        }

        response = requests.get(BASE_URL, headers=headers, params=params)
        data = response.json()

        print("Status code:", response.status_code)

        # We'll print a brief summary each page
        pagination = data.get("pagination", {})
        total_items = pagination.get("total_items", 0)
        print(f"Fetched page {page} of {pagination.get('max_page', 0)} (total_items={total_items})")

        # Append the bills (usually in data["results"] or data["data"])
        results = data.get("results", [])
        all_bills.extend(results)

        # Update pagination logic
        per_page = pagination.get("per_page", 50)
        total_pages = math.ceil(total_items / per_page)
        page += 1

        # Safety break if we see no more results
        if total_pages == 0:
            break

    return all_bills

if __name__ == "__main__":
    bills = fetch_privacy_bills()
    print(f"Total bills fetched: {len(bills)}")

    # --- SAVE TO A LOCAL JSON FILE ---
    # This will create the file if it doesn't exist, or overwrite if it does.
    with open("privacy_bills.json", "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=2)

    print("Data saved to privacy_bills.json")

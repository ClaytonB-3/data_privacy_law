import requests
import json
import math
import time

API_KEY = "03638390-ffa9-463e-9782-c94b4073565a"  # Replace with your own
BASE_URL = "https://v3.openstates.org/bills"

def build_or_query(terms):
    """
    Given a list of search terms, build a query string using OR logic.
    Example: ["foo", "bar"] -> '"foo" OR "bar"'
    """
    # Surround each term in quotes in case of multi-word phrases
    quoted_terms = [f'"{term}"' for term in terms]
    return " OR ".join(quoted_terms)

def get_bill_info(bill):
    """
    Extract the fields we care about from the raw bill data:
      - title
      - status (simple approximation from latest action)
      - abstract (if available)
      - details (OpenStates URL or other links)
      - affected parties (from subject array, if any)
    """
    info = {}

    # Title
    info["title"] = bill.get("title", "")

    # Status: This is not standardized in v3, so let's approximate from the latest action
    latest_action = bill.get("latest_action_description", "")
    # You might further parse or match certain text to guess if the bill is "enacted", etc.
    # We'll just store the raw "latest_action_description" for now.
    # Alternatively, if the API had a "status" field, you could use that directly.
    info["status"] = latest_action if latest_action else "Unknown"

    # Abstract: Some bills have a short abstract in "summary" or "extras" or "abstract".
    # There's no guarantee. We'll look in a couple of places:
    info["abstract"] = ""
    if "abstract" in bill:
        info["abstract"] = bill["abstract"]
    elif "extras" in bill and "bill_summary" in bill["extras"]:
        info["abstract"] = bill["extras"]["bill_summary"]
    # Adjust as needed based on actual data.

    # Details: We'll grab the openstates.org link
    info["details"] = bill.get("openstates_url", "")

    # Affected parties: We often use 'subject' as a proxy
    info["affected_parties"] = bill.get("subject", [])

    return info

def fetch_ca_privacy_bills():
    # Define our key terms
    search_terms = [
        "Personal Data protection",
        "Consumer data protection",
        "Healthcare private data",
        "Financial data privacy",
        "Child data privacy",
        "AI data regulations"
    ]
    
    # Build a single OR-based query
    query_str = build_or_query(search_terms)

    all_bills = []
    page = 1
    per_page = 20
    total_pages = 1

    while page <= total_pages:
        params = {
            "apikey": API_KEY,             # or use headers = {"X-API-KEY": API_KEY}
            "jurisdiction": "California",  # <--- searching only in California
            "q": query_str,
            "page": page,
            "per_page": per_page
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 429:
            # Rate limit hit; wait and retry
            print("Rate limit hit. Waiting 30 seconds...")
            time.sleep(30)
            continue  # retry same page

        print("Status code:", response.status_code)
        
        data = response.json()
        pagination = data.get("pagination", {})
        total_items = pagination.get("total_items", 0)
        max_page = pagination.get("max_page", 1)

        print(f"Fetched page {page} of {max_page} (total_items={total_items})")

        results = data.get("results", [])

        # Extract the fields we want from each bill
        for bill in results:
            bill_info = get_bill_info(bill)
            all_bills.append(bill_info)

        # Update pagination
        total_pages = math.ceil(total_items / per_page)
        page += 1

        # Polite delay to avoid rate limits
        time.sleep(1)

        # Safety check
        if total_pages == 0:
            break

    return all_bills

if __name__ == "__main__":
    bills = fetch_ca_privacy_bills()
    print(f"Total bills fetched: {len(bills)}")

    # Save to a local JSON file
    with open("california_privacy_bills.json", "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=2)

    print("Data saved to california_privacy_bills.json")

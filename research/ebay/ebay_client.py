import os, base64, time, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["EBAY_CLIENT_ID"]
CLIENT_SECRET = os.environ["EBAY_CLIENT_SECRET"]
MARKETPLACE = "EBAY_GB"          # or EBAY_DE / EBAY_US
WRISTWATCH_CATEGORY = "31387"

_token = {"value": None, "expires": 0}


def get_token():
    """Application token via client credentials. Cached until ~2h expiry."""
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]

    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={"Authorization": f"Basic {creds}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials",
              "scope": "https://api.ebay.com/oauth/api_scope"},
        timeout=30,
    )
    if r.status_code != 200:
        print("STATUS:", r.status_code)
        print("BODY:", r.text)
        r.raise_for_status()
    d = r.json()
    _token["value"] = d["access_token"]
    _token["expires"] = time.time() + d["expires_in"]
    return _token["value"]


def headers():
    return {"Authorization": f"Bearer {get_token()}",
            "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE}


def category_tree_id():
    r = requests.get(
        "https://api.ebay.com/commerce/taxonomy/v1/get_default_category_tree_id",
        headers=headers(), params={"marketplace_id": MARKETPLACE}, timeout=30)
    r.raise_for_status()
    return r.json()["categoryTreeId"]


def watch_aspects():
    """The real field names eBay supports for wristwatches."""
    tree = category_tree_id()
    r = requests.get(
        f"https://api.ebay.com/commerce/taxonomy/v1/category_tree/{tree}"
        "/get_item_aspects_for_category",
        headers=headers(), params={"category_id": WRISTWATCH_CATEGORY}, timeout=30)
    r.raise_for_status()
    return r.json().get("aspects", [])


def search_watches(query=None, limit=10, offset=0, extra_filter=None):
    params = {"category_ids": WRISTWATCH_CATEGORY,
              "limit": limit, "offset": offset}
    if query:
        params["q"] = query
    if extra_filter:
        params["filter"] = extra_filter

    r = requests.get("https://api.ebay.com/buy/browse/v1/item_summary/search",
                     headers=headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_item(item_id):
    """Full detail including localizedAspects (reference number, materials...)."""
    r = requests.get(f"https://api.ebay.com/buy/browse/v1/item/{item_id}",
                     headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("Token OK:", get_token()[:25], "...\n")

    print("--- ASPECTS ---")
    for a in watch_aspects():
        c = a.get("aspectConstraint", {})
        flag = "required" if c.get("aspectRequired") else "optional"
        print(f"  {a['localizedAspectName']:<28} {flag}")

    print("\n--- SAMPLE LISTINGS ---")
    data = search_watches(query="Rolex Submariner", limit=5)
    print(f"total matches: {data.get('total')}\n")

    for it in data.get("itemSummaries", []):
        print(it["title"][:70])
        print("  ", it["price"]["value"], it["price"]["currency"], "|", it["itemId"])

    ids = [i["itemId"] for i in data.get("itemSummaries", [])]
    if ids:
        print("\n--- ASPECTS ON ONE REAL WATCH ---")
        for a in get_item(ids[0]).get("localizedAspects", []):
            print(f"  {a['name']}: {a['value']}")
#!/usr/bin/env python3
"""
ebay_diagnostic2.py — Round two. Tests the assumptions the crawler depends on.

Round one told us what data exists. This one tests whether the plan to
collect it actually works, before you build on top of it.

  T1  Bulk endpoint          does /item?item_ids= work, and how many IDs?
  T2  Field parity           does bulk return the same aspects as single?
  T3  Brand filter           fixed, case-exact, with verification
  T4  Price partitioning     can Rolex be split under the 10k ceiling?
  T5  Churn                  how much of the category is new each day?
  T6  Listing formats        auction vs fixed price (auction = clean outcome)
  T7  Coverage by tier       does data quality track price?
  T8  Junk detection         how well do non-standard aspects flag rubbish?

Usage:
    python ebay_diagnostic2.py                    # ~120 calls
    python ebay_diagnostic2.py --test T1 T2       # just the critical two
    python ebay_diagnostic2.py --marketplace EBAY_US
"""

import argparse
import base64
import json
import os
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")
CAT = "31387"
OUT = Path("diagnostic_output")

BASE = "https://api.ebay.com/buy/browse/v1"
SEARCH = f"{BASE}/item_summary/search"
ITEM = f"{BASE}/item"

# The official 45-aspect schema from round one. Anything outside this set
# is a seller inventing fields — a strong junk signal.
OFFICIAL_ASPECTS = {
    "Brand", "Department", "Reference Number", "Customised", "Model",
    "Dial Colour", "Strap Colour", "Case Colour", "Movement", "Features",
    "Strap Material", "Case Material", "Style", "Display", "Year Manufactured",
    "Type", "With Papers", "With Original Box/Packaging", "Water Resistance",
    "Indices", "Bezel Colour", "Case Size", "Band/Strap", "Watch Shape",
    "Vintage", "Bezel Type", "Dial Pattern", "Country of Origin", "Theme",
    "Caseback", "Strap Width", "Lug Width", "Number of Jewels",
    "With Manual/Booklet", "Seller Warranty", "With Service Records",
    "Handmade", "Case Finish", "Escapement Type", "Case Thickness",
    "Max Wrist Size", "Manufacturer Warranty", "Closure", "Handedness",
    "Unit Quantity", "Unit Type",
}

LUXURY_TARGETS = [
    "Rolex", "OMEGA", "TAG Heuer", "Cartier", "Longines", "Breitling",
    "TUDOR", "IWC", "Panerai", "Audemars Piguet", "Patek Philippe",
]

CRITICAL = ["Brand", "Model", "Reference Number", "Case Material",
            "Movement", "Case Size", "Year Manufactured"]

CALLS = Counter()
_token = {"value": None, "expires": 0}


def token():
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]
    if not CLIENT_ID or not CLIENT_SECRET:
        sys.exit("  Missing EBAY_CLIENT_ID / EBAY_CLIENT_SECRET in .env")
    c = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post("https://api.ebay.com/identity/v1/oauth2/token",
                      headers={"Authorization": f"Basic {c}",
                               "Content-Type": "application/x-www-form-urlencoded"},
                      data={"grant_type": "client_credentials",
                            "scope": "https://api.ebay.com/oauth/api_scope"},
                      timeout=30)
    if r.status_code != 200:
        sys.exit(f"  Auth failed [{r.status_code}]: {r.text[:300]}")
    d = r.json()
    _token["value"] = d["access_token"]
    _token["expires"] = time.time() + d.get("expires_in", 7200)
    return _token["value"]


def get(url, mk, label, **params):
    h = {"Authorization": f"Bearer {token()}", "X-EBAY-C-MARKETPLACE-ID": mk}
    try:
        r = requests.get(url, headers=h, params=params or None, timeout=45)
    except requests.RequestException as e:
        return None, 0, str(e)
    CALLS[label] += 1
    if r.status_code != 200:
        return None, r.status_code, r.text[:300]
    try:
        return r.json(), 200, None
    except ValueError:
        return None, r.status_code, "bad json"


def head(n, title):
    print(f"\n{'=' * 68}\n  T{n}. {title}\n{'=' * 68}")


def sample_ids(mk, brand=None, n=40):
    """Grab n item IDs to work with."""
    p = {"category_ids": CAT, "limit": min(n, 200)}
    if brand:
        p["aspect_filter"] = f"categoryId:{CAT},Brand:{{{brand}}}"
    d, st, err = get(SEARCH, mk, "search", **p)
    return [i["itemId"] for i in (d or {}).get("itemSummaries", [])][:n]


# ------------------------------------------------------------------ T1

def t1_bulk(mk, res):
    head(1, "BULK ENDPOINT — does it work, and how many IDs per call?")
    print("  Everything about crawl capacity depends on this.\n")

    ids = sample_ids(mk, n=25)
    if not ids:
        print("  Could not get sample IDs. Aborting test.")
        return

    found = 0
    for size in (2, 5, 10, 20, 25):
        batch = ids[:size]
        if len(batch) < size:
            break
        d, st, err = get(ITEM, mk, "getItems", item_ids=",".join(batch))
        got = len((d or {}).get("items", []) or [])
        ok = st == 200
        print(f"   {size:>3} ids -> status {st}   returned {got}"
              f"   {'ok' if ok else 'FAIL'}")
        if not ok and err:
            print(f"        {err[:150]}")
        if ok:
            found = size

    if found:
        print(f"\n   Max confirmed batch size: {found}")
        print(f"   Effective detail capacity: 5,000 calls x {found}"
              f" = {5000*found:,} items/day")
    else:
        print("\n   Bulk endpoint unavailable. Capacity stays at 5,000/day")
        print("   and the luxury sweep takes ~36 days instead of 2.")

    res["bulk_max"] = found


# ------------------------------------------------------------------ T2

def t2_parity(mk, res):
    head(2, "FIELD PARITY — does bulk return the same data as single?")
    print("  If bulk drops localizedAspects, the capacity win is worthless.\n")

    ids = sample_ids(mk, brand="Rolex", n=5)
    if not ids:
        print("  No sample. Skipping.")
        return

    bulk, st, err = get(ITEM, mk, "getItems", item_ids=",".join(ids))
    if not bulk:
        print(f"  Bulk call failed ({st}). Skipping parity check.")
        return

    bulk_by_id = {i.get("itemId"): i for i in bulk.get("items", []) or []}
    diffs = []

    for iid in ids[:3]:
        single, st2, _ = get(f"{ITEM}/{iid}", mk, "getItem")
        if not single:
            continue
        b = bulk_by_id.get(iid, {})
        sa = {a["name"] for a in single.get("localizedAspects", []) or []}
        ba = {a["name"] for a in b.get("localizedAspects", []) or []}
        sk, bk = set(single), set(b)
        diffs.append({"item": iid, "aspects_single": len(sa),
                      "aspects_bulk": len(ba),
                      "missing_aspects": sorted(sa - ba),
                      "missing_top_level": sorted(sk - bk)})
        print(f"   {iid}")
        print(f"      aspects: single={len(sa)}  bulk={len(ba)}")
        if sa - ba:
            print(f"      bulk missing aspects: {', '.join(sorted(sa - ba))[:90]}")
        if sk - bk:
            print(f"      bulk missing fields:  {', '.join(sorted(sk - bk))[:90]}")

    total_missing = sum(len(d["missing_aspects"]) for d in diffs)
    print(f"\n   Verdict: {'IDENTICAL aspects — use bulk everywhere'
                          if total_missing == 0 else
                          'bulk is lossy — check what you actually need'}")
    res["parity"] = diffs


# ------------------------------------------------------------------ T3

def t3_brandfilter(mk, res):
    head(3, "BRAND FILTER — case-exact, with verification")
    print("  Round one failed silently on 'Omega' (eBay stores 'OMEGA').")
    print("  Pulling exact strings from refinements and verifying results.\n")

    d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                   fieldgroups="ASPECT_REFINEMENTS")
    official = {}
    for ad in (d or {}).get("refinement", {}).get("aspectDistributions", []):
        if ad.get("localizedAspectName") == "Brand":
            official = {v["localizedAspectValue"]: v["matchCount"]
                        for v in ad.get("aspectValueDistributions", [])}

    lookup = {k.lower(): k for k in official}
    verified = {}

    for want in LUXURY_TARGETS:
        exact = lookup.get(want.lower())
        if not exact:
            print(f"   {want:<18} NOT FOUND in refinements")
            continue

        d2, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=20,
                       aspect_filter=f"categoryId:{CAT},Brand:{{{exact}}}")
        items = (d2 or {}).get("itemSummaries", []) or []
        # verify by pulling brand back out of the titles we got
        hits = sum(1 for i in items
                   if exact.lower().split()[0] in i.get("title", "").lower())
        purity = round(hits / len(items) * 100, 1) if items else 0
        flag = "" if purity >= 70 else "   <-- filter may be ignored"
        note = f" (you wrote '{want}')" if exact != want else ""
        print(f"   {exact:<18} {official[exact]:>7,} listings"
              f"   purity {purity:>5.1f}%{flag}{note}")
        verified[exact] = {"count": official[exact], "purity": purity}

    total = sum(v["count"] for v in verified.values())
    print(f"\n   Luxury target pool: {total:,} listings")
    res["brands"] = verified


# ------------------------------------------------------------------ T4

def t4_partition(mk, res):
    head(4, "PRICE PARTITIONING — can big brands be sliced under 10k?")
    print("  Rolex is ~52k listings, ceiling is 10k per query.\n")

    bands = [(0, 500), (500, 1500), (1500, 3000), (3000, 6000),
             (6000, 10000), (10000, 20000), (20000, 50000), (50000, None)]

    for brand in ("Rolex", "OMEGA"):
        print(f"   {brand}")
        over = 0
        for lo, hi in bands:
            rng = f"[{lo}..{hi}]" if hi else f"[{lo}]"
            d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                           aspect_filter=f"categoryId:{CAT},Brand:{{{brand}}}",
                           filter=f"price:{rng},priceCurrency:GBP")
            n = (d or {}).get("total", 0)
            mark = "  OVER CEILING" if n > 10000 else ""
            over += 1 if n > 10000 else 0
            label = f"{lo}-{hi}" if hi else f"{lo}+"
            print(f"      {label:<14} {n:>8,}{mark}")
        print(f"      -> {over} band(s) need further splitting\n")

    print("   Bands over 10k can be split again by condition, or by")
    print("   Model, or by buyingOptions. Recurse until every slice fits.")


# ------------------------------------------------------------------ T5

def t5_churn(mk, res):
    head(5, "CHURN — how much is new each day?")
    print("  Decides whether daily crawling is necessary or wasteful.\n")

    now = datetime.now(timezone.utc)
    for label, days in (("last 24h", 1), ("last 7d", 7), ("last 30d", 30)):
        since = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                         filter=f"itemStartDate:[{since}]")
        n = (d or {}).get("total", 0)
        if st != 200:
            print(f"   {label:<10} filter unsupported ({st})")
            continue
        print(f"   {label:<10} {n:>10,} new listings")
        res.setdefault("churn", {})[label] = n

    base, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1)
    total = (base or {}).get("total", 0)
    daily = res.get("churn", {}).get("last 24h", 0)
    if total and daily:
        print(f"\n   Daily turnover: {daily/total*100:.2f}% of the category")
        print(f"   A daily 'new listings only' crawl would cost roughly")
        print(f"   {daily//20:,} bulk calls — trivially affordable.")


# ------------------------------------------------------------------ T6

def t6_formats(mk, res):
    head(6, "LISTING FORMATS — auctions give clean outcomes")
    print("  An auction that ends has a definite result. A fixed-price")
    print("  listing that vanishes is ambiguous: sold, or just withdrawn?\n")

    for opt in ("AUCTION", "FIXED_PRICE", "BEST_OFFER"):
        d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                       filter=f"buyingOptions:{{{opt}}}")
        n = (d or {}).get("total", 0)
        print(f"   {opt:<14} {n:>10,}")
        res.setdefault("formats", {})[opt] = n

    for brand in ("Rolex", "OMEGA"):
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                      aspect_filter=f"categoryId:{CAT},Brand:{{{brand}}}",
                      filter="buyingOptions:{AUCTION}")
        print(f"   {brand} auctions: {(d or {}).get('total', 0):,}")


# ------------------------------------------------------------------ T7 + T8

def t7_tiers(mk, res, per_tier=12):
    head(7, "COVERAGE BY PRICE TIER + JUNK DETECTION")
    print("  Does data quality track price? And do non-standard aspect")
    print("  names reliably identify rubbish listings?\n")

    tiers = [("budget", "[0..100]"), ("mid", "[100..1000]"),
             ("luxury", "[1000..10000]"), ("high-end", "[10000..100000]")]

    summary = {}
    for name, rng in tiers:
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT,
                      limit=per_tier,
                      filter=f"price:{rng},priceCurrency:GBP")
        ids = [i["itemId"] for i in (d or {}).get("itemSummaries", [])]
        if not ids:
            continue

        counts = Counter()
        junk_flags = 0
        nonstandard = Counter()
        n = 0

        bulkmax = res.get("bulk_max") or 1
        for i in range(0, len(ids), max(bulkmax, 1)):
            chunk = ids[i:i + max(bulkmax, 1)]
            if bulkmax > 1:
                d2, _, _ = get(ITEM, mk, "getItems", item_ids=",".join(chunk))
                items = (d2 or {}).get("items", []) or []
            else:
                items = []
                for iid in chunk:
                    s, _, _ = get(f"{ITEM}/{iid}", mk, "getItem")
                    if s:
                        items.append(s)

            for it in items:
                n += 1
                names = {a["name"] for a in it.get("localizedAspects", []) or []}
                for nm in names:
                    counts[nm] += 1
                odd = names - OFFICIAL_ASPECTS
                if odd:
                    junk_flags += 1
                    for o in odd:
                        nonstandard[o] += 1

        if not n:
            continue

        crit = {f: round(counts.get(f, 0) / n * 100, 1) for f in CRITICAL}
        avg = round(sum(counts.values()) / n, 1)
        print(f"   {name:<10} n={n:<3} avg fields/item={avg:<5}"
              f" junk-flagged={junk_flags}/{n}")
        print(f"      ref#={crit['Reference Number']:>5.1f}%"
              f"  model={crit['Model']:>5.1f}%"
              f"  case-mat={crit['Case Material']:>5.1f}%"
              f"  year={crit['Year Manufactured']:>5.1f}%")
        summary[name] = {"n": n, "avg_fields": avg, "critical": crit,
                         "junk_flagged": junk_flags}

    if summary:
        print("\n   Reading: if luxury tiers show materially better coverage,")
        print("   scope the project there and ignore the long tail.")

    head(8, "NON-STANDARD ASPECT NAMES SEEN")
    if nonstandard:
        for nm, c in nonstandard.most_common(15):
            print(f"   {c:>3}x  {nm}")
        print("\n   These are outside eBay's 45-aspect schema — sellers")
        print("   inventing fields. Presence of any is a usable junk filter.")
    else:
        print("   None seen in this sample.")

    res["tiers"] = summary
    res["nonstandard_aspects"] = dict(nonstandard.most_common(40))


# ------------------------------------------------------------------ main

TESTS = {"T1": t1_bulk, "T2": t2_parity, "T3": t3_brandfilter,
         "T4": t4_partition, "T5": t5_churn, "T6": t6_formats, "T7": t7_tiers}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--marketplace", default="EBAY_GB")
    p.add_argument("--test", nargs="*", default=list(TESTS),
                   help="e.g. --test T1 T2")
    a = p.parse_args()

    OUT.mkdir(exist_ok=True)
    res = {"run_at": datetime.now(timezone.utc).isoformat(),
           "marketplace": a.marketplace}

    print(f"\n  Round-two diagnostic  |  {a.marketplace}")
    token()
    print("  auth ok")

    # T1 must run first — T2 and T7 use its result.
    order = [t for t in ("T1", "T2", "T3", "T4", "T5", "T6", "T7")
             if t in a.test]
    for t in order:
        try:
            TESTS[t](a.marketplace, res)
        except Exception as e:
            print(f"\n  {t} crashed: {type(e).__name__}: {e}")

    print(f"\n{'=' * 68}\n  CALLS USED: {sum(CALLS.values())}\n{'=' * 68}")
    for k, v in CALLS.most_common():
        print(f"   {v:>5}  {k}")

    res["calls"] = dict(CALLS)
    with open(OUT / "report2.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n  -> {OUT / 'report2.json'}\n")


if __name__ == "__main__":
    main()
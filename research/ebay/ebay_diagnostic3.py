#!/usr/bin/env python3
"""
ebay_diagnostic3.py — Round three. Verifies the crawler design itself.

Round one: what data exists.
Round two: killed the bulk-endpoint plan.
Round three: tests every assumption the search-first design rests on,
before a line of crawler code gets written.

  T1  Search page size        is limit really 200?
  T2  Summary field inventory what do you get free vs what needs getItem?
  T3  Search fieldgroups      can fieldgroups add data at no extra cost?
  T4  Filter composability    does aspect + date + price + sort combine?
  T5  Deep pagination         does offset still work with filters applied?
  T6  Partition completeness  the 2% Rolex leak — where does it go?
  T7  Title parsing           can regex recover refs from titles?
  T8  Rate limit accounting   does 1 request really cost 1 call?
  T9  Item ID structure       variations, duplicates, primary key safety
  T10 Condition + images      distribution and availability

Usage:
    python ebay_diagnostic3.py
    python ebay_diagnostic3.py --test T6 T7
    python ebay_diagnostic3.py --marketplace EBAY_US --currency USD
"""

import argparse
import base64
import json
import os
import re
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
RATELIMIT = "https://api.ebay.com/developer/analytics/v1_beta/rate_limit/"

CALLS = Counter()
_token = {"value": None, "expires": 0}


def token():
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]
    if not CLIENT_ID or not CLIENT_SECRET:
        sys.exit("  Missing credentials in .env")
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
        r = requests.get(url, headers=h, params=params or None, timeout=60)
    except requests.RequestException as e:
        return None, 0, str(e)
    CALLS[label] += 1
    if r.status_code != 200:
        return None, r.status_code, r.text[:400]
    try:
        return r.json(), 200, None
    except ValueError:
        return None, r.status_code, "bad json"


def head(n, title):
    print(f"\n{'=' * 70}\n  T{n}. {title}\n{'=' * 70}")


def brand_filter(brand):
    return f"categoryId:{CAT},Brand:{{{brand}}}"


# ------------------------------------------------------------------ T1

def t1_pagesize(mk, cur, res):
    head(1, "SEARCH PAGE SIZE — is limit really 200?")
    print("  The whole 911-calls-per-sweep figure depends on this.\n")

    best = 0
    for lim in (50, 100, 200, 201, 500):
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, limit=lim)
        got = len((d or {}).get("itemSummaries", []) or [])
        if st == 200:
            best = max(best, got)
            print(f"   limit={lim:<4} -> returned {got}")
        else:
            print(f"   limit={lim:<4} -> {st}  {(err or '')[:80]}")

    res["max_page"] = best
    if best:
        pool = 182177
        print(f"\n   Max page size: {best}")
        print(f"   Luxury pool sweep: {-(-pool // best):,} calls"
              f"  ({-(-pool // best) / 5000 * 100:.1f}% of daily budget)")


# ------------------------------------------------------------------ T2

def t2_summary_fields(mk, cur, res):
    head(2, "SUMMARY vs DETAIL — what do you get without getItem?")
    print("  Every field available in search is a getItem call you skip.\n")

    d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=5,
                   aspect_filter=brand_filter("Rolex"))
    items = (d or {}).get("itemSummaries", []) or []
    if not items:
        print("  No results.")
        return

    keys = Counter()
    for i in items:
        keys.update(i.keys())

    print(f"   Fields present in item_summary (n={len(items)}):")
    for k, c in sorted(keys.items()):
        always = "always" if c == len(items) else f"{c}/{len(items)}"
        print(f"      {k:<28} {always}")

    sample = items[0]
    detail, st2, _ = get(f"{ITEM}/{sample['itemId']}", mk, "getItem")
    if detail:
        only_detail = sorted(set(detail) - set(sample))
        print(f"\n   Fields ONLY in getItem ({len(only_detail)}):")
        for k in only_detail:
            star = "  <-- the reason enrichment exists" \
                if k == "localizedAspects" else ""
            print(f"      {k}{star}")

    # things the crawler specifically wants
    wanted = ["itemCreationDate", "condition", "conditionId", "image",
              "thumbnailImages", "seller", "buyingOptions", "itemWebUrl",
              "itemLocation", "bidCount", "currentBidPrice", "priceDisplay"]
    print("\n   Crawler-relevant fields in summary:")
    for w in wanted:
        print(f"      {'YES' if w in keys else ' - ':<4} {w}")

    res["summary_fields"] = dict(keys)
    res["detail_only_fields"] = sorted(set(detail or {}) - set(sample))


# ------------------------------------------------------------------ T3

def t3_fieldgroups(mk, cur, res):
    head(3, "SEARCH FIELDGROUPS — free extra data?")
    print("  If a fieldgroup adds fields at no call cost, always use it.\n")

    baseline, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=3)
    base_keys = set()
    for i in (baseline or {}).get("itemSummaries", []) or []:
        base_keys |= set(i)

    for fg in ("EXTENDED", "MATCHING_ITEMS", "FULL",
               "ASPECT_REFINEMENTS", "CATEGORY_REFINEMENTS"):
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, limit=3,
                         fieldgroups=fg)
        if st != 200:
            print(f"   {fg:<22} {st}  {(err or '')[:60]}")
            continue
        ks = set()
        for i in (d or {}).get("itemSummaries", []) or []:
            ks |= set(i)
        extra = sorted(ks - base_keys)
        has_ref = "refinement" in (d or {})
        print(f"   {fg:<22} ok   extra item fields: "
              f"{', '.join(extra) if extra else 'none'}"
              f"{'   + refinement block' if has_ref else ''}")


# ------------------------------------------------------------------ T4

def t4_composability(mk, cur, res):
    head(4, "FILTER COMPOSABILITY — does the incremental crawl work?")
    print("  The daily design needs brand + date + price + sort together.\n")

    since = (datetime.now(timezone.utc) - timedelta(days=1)
             ).strftime("%Y-%m-%dT%H:%M:%SZ")

    combos = [
        ("brand only", {"aspect_filter": brand_filter("Rolex")}),
        ("brand + price", {"aspect_filter": brand_filter("Rolex"),
                           "filter": f"price:[1000..5000],priceCurrency:{cur}"}),
        ("brand + date", {"aspect_filter": brand_filter("Rolex"),
                          "filter": f"itemStartDate:[{since}]"}),
        ("brand + date + price",
         {"aspect_filter": brand_filter("Rolex"),
          "filter": f"itemStartDate:[{since}],price:[1000..5000],"
                    f"priceCurrency:{cur}"}),
        ("brand + sort newlyListed",
         {"aspect_filter": brand_filter("Rolex"), "sort": "newlyListed"}),
        ("brand + date + sort",
         {"aspect_filter": brand_filter("Rolex"),
          "filter": f"itemStartDate:[{since}]", "sort": "newlyListed"}),
        ("brand + condition",
         {"aspect_filter": brand_filter("Rolex"),
          "filter": "conditions:{USED}"}),
        ("brand + buyingOptions",
         {"aspect_filter": brand_filter("Rolex"),
          "filter": "buyingOptions:{AUCTION}"}),
    ]

    for name, p in combos:
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, limit=2, **p)
        if st != 200:
            print(f"   {name:<26} FAIL {st}  {(err or '')[:70]}")
            continue
        total = (d or {}).get("total", 0)
        n = len((d or {}).get("itemSummaries", []) or [])
        print(f"   {name:<26} ok   total={total:>8,}  returned={n}")

    print("\n   If 'brand + date + sort' works, the daily incremental")
    print("   crawl is viable and cheap. If it fails, you must sweep")
    print("   everything every day and diff locally.")


# ------------------------------------------------------------------ T5

def t5_deep_paging(mk, cur, res):
    head(5, "DEEP PAGINATION WITH FILTERS")
    print("  Round one tested bare category. Filters may behave differently.\n")

    pf = {"aspect_filter": brand_filter("Rolex")}
    for offset in (0, 2000, 5000, 9800, 9900, 10000):
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, limit=10,
                         offset=offset, **pf)
        got = len((d or {}).get("itemSummaries", []) or [])
        print(f"   offset {offset:>6}  ->  {got} items"
              f"   {'ok' if got else f'blocked ({st})'}")

    print("\n   Reachable per query is what matters, not the reported total.")


# ------------------------------------------------------------------ T6

def t6_partition_leak(mk, cur, res):
    head(6, "PARTITION COMPLETENESS — where do the missing 2% go?")
    print("  Rolex bands summed to 50,739 but the brand total is 51,804.")
    print("  Finding the leak matters: silent data loss is the worst kind.\n")

    for brand in ("Rolex", "OMEGA"):
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                      aspect_filter=brand_filter(brand))
        total = (d or {}).get("total", 0)

        bands = [(0, 500), (500, 1500), (1500, 3000), (3000, 6000),
                 (6000, 10000), (10000, 20000), (20000, 50000), (50000, None)]
        summed = 0
        for lo, hi in bands:
            rng = f"[{lo}..{hi}]" if hi else f"[{lo}]"
            d2, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                           aspect_filter=brand_filter(brand),
                           filter=f"price:{rng},priceCurrency:{cur}")
            summed += (d2 or {}).get("total", 0)

        # same partition WITHOUT the currency constraint
        nocur = 0
        for lo, hi in bands:
            rng = f"[{lo}..{hi}]" if hi else f"[{lo}]"
            d3, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                           aspect_filter=brand_filter(brand),
                           filter=f"price:{rng}")
            nocur += (d3 or {}).get("total", 0)

        # auctions, a likely home for price-less listings
        d4, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                       aspect_filter=brand_filter(brand),
                       filter="buyingOptions:{AUCTION}")
        auctions = (d4 or {}).get("total", 0)

        gap = total - summed
        print(f"   {brand}")
        print(f"      brand total                 {total:>8,}")
        print(f"      sum of bands (with {cur})   {summed:>8,}")
        print(f"      sum of bands (no currency)  {nocur:>8,}")
        print(f"      auctions in brand           {auctions:>8,}")
        print(f"      LEAK                        {gap:>8,}"
              f"  ({gap/total*100:.2f}%)")
        if nocur > summed:
            print(f"      -> dropping priceCurrency recovers {nocur-summed:,}")
        print()

    print("   Whatever the cause, the crawler must assert that partition")
    print("   sums match the parent total, and widen or add an overflow")
    print("   slice when they don't.")


# ------------------------------------------------------------------ T7

REF_PATTERNS = [
    r"\b(\d{4,6}[A-Z]{0,3}(?:-\d{4})?)\b",        # 116610LN, 16610, 5513
    r"\b([A-Z]{2,4}\d{3,4}\.[A-Z]{2}\d{4})\b",     # CAZ1014.BA0842
    r"\b(\d{4}\.\d{2}\.\d{2})\b",                  # 1502.30.00
    r"\b([A-Z]\d{4}[A-Z]?)\b",                     # misc
]


def extract_ref(title):
    for pat in REF_PATTERNS:
        m = re.search(pat, title)
        if m:
            return m.group(1)
    return None


def t7_title_parsing(mk, cur, res, n=40):
    head(7, "TITLE PARSING — can regex recover reference numbers?")
    print("  If yes, unenriched listings still get a usable reference.\n")

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=n,
                  aspect_filter=brand_filter("Rolex"))
    ids = [(i["itemId"], i.get("title", ""))
           for i in (d or {}).get("itemSummaries", [])][:n]

    have_both = exact = partial = miss = 0
    no_aspect_but_title = 0
    examples = []

    for iid, title in ids:
        det, st, _ = get(f"{ITEM}/{iid}", mk, "getItem")
        if not det:
            continue
        asp = {a["name"]: a["value"]
               for a in det.get("localizedAspects", []) or []}
        true_ref = asp.get("Reference Number")
        guess = extract_ref(title)

        if true_ref and guess:
            have_both += 1
            t = true_ref.upper().replace(" ", "")
            g = guess.upper().replace(" ", "")
            if g in t or t in g:
                exact += 1
            elif any(g in part or part in g for part in t.split(",")):
                partial += 1
            else:
                miss += 1
                if len(examples) < 6:
                    examples.append((title[:52], true_ref[:24], guess))
        elif guess and not true_ref:
            no_aspect_but_title += 1

    tot = max(have_both, 1)
    print(f"   items with both aspect ref and title guess: {have_both}")
    print(f"      exact/contained match  {exact:>3}  ({exact/tot*100:.0f}%)")
    print(f"      partial (multi-ref)    {partial:>3}  ({partial/tot*100:.0f}%)")
    print(f"      wrong                  {miss:>3}  ({miss/tot*100:.0f}%)")
    print(f"\n   listings with NO aspect ref but a parseable title ref:"
          f" {no_aspect_but_title}")
    print("      ^ these are pure gain — data you would otherwise lose")

    if examples:
        print("\n   Mismatches worth eyeballing:")
        for t, tr, g in examples:
            print(f"      title: {t}")
            print(f"        aspect={tr}   regex={g}")

    res["title_parsing"] = {"both": have_both, "exact": exact,
                            "partial": partial, "wrong": miss,
                            "title_only": no_aspect_but_title}


# ------------------------------------------------------------------ T8

def t8_ratelimit_cost(mk, cur, res):
    head(8, "RATE LIMIT ACCOUNTING — does 1 request cost 1 call?")
    print("  Your entire budget model assumes it does. Measuring.\n")

    def browse_remaining():
        d, _, _ = get(RATELIMIT, mk, "ratelimit")
        for g in (d or {}).get("rateLimits", []):
            for r_ in g.get("resources", []):
                if r_.get("name") == "buy.browse":
                    for rate in r_.get("rates", []):
                        return rate.get("remaining")
        return None

    before = browse_remaining()
    N = 5
    for _ in range(N):
        get(SEARCH, mk, "search", category_ids=CAT, limit=1)
    after = browse_remaining()

    if before is None or after is None:
        print("   Could not read buy.browse remaining.")
        return

    used = before - after
    print(f"   remaining before : {before:,}")
    print(f"   made {N} search calls")
    print(f"   remaining after  : {after:,}")
    print(f"   consumed         : {used}  (expected ~{N})")
    if used > N:
        print("   -> costs MORE than 1 per request; recalculate budgets")
    elif used < N:
        print("   -> some calls cached or free; budget is better than assumed")
    else:
        print("   -> 1:1 as assumed")

    res["ratelimit_cost"] = {"before": before, "after": after,
                             "calls": N, "consumed": used}


# ------------------------------------------------------------------ T9

def t9_item_ids(mk, cur, res, n=100):
    head(9, "ITEM ID STRUCTURE — is it a safe primary key?")
    print("  Round one saw 'v1|398355617944|666609637473' — a variation.\n")

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=n,
                  aspect_filter=brand_filter("Rolex"))
    items = (d or {}).get("itemSummaries", []) or []

    variations = 0
    legacy_groups = defaultdict(int)
    dupes = Counter()

    for i in items:
        iid = i.get("itemId", "")
        dupes[iid] += 1
        parts = iid.split("|")
        if len(parts) >= 3 and parts[2] not in ("0", ""):
            variations += 1
        if len(parts) >= 2:
            legacy_groups[parts[1]] += 1

    multi = {k: v for k, v in legacy_groups.items() if v > 1}
    print(f"   sampled                     {len(items)}")
    print(f"   variation items (suffix!=0) {variations}")
    print(f"   duplicate full itemIds      {sum(1 for v in dupes.values() if v>1)}")
    print(f"   legacy IDs appearing twice+ {len(multi)}")
    if multi:
        print("      e.g.", list(multi.items())[:3])
    print("\n   Use the full itemId string as primary key. The middle")
    print("   segment groups variations of one listing — store it")
    print("   separately if you want to collapse them.")

    res["item_ids"] = {"sampled": len(items), "variations": variations,
                       "multi_variation_listings": len(multi)}


# ------------------------------------------------------------------ T10

def t10_condition_images(mk, cur, res):
    head(10, "CONDITION DISTRIBUTION + IMAGE AVAILABILITY")
    print()

    for cond in ("NEW", "USED", "UNSPECIFIED"):
        d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                       aspect_filter=brand_filter("Rolex"),
                       filter=f"conditions:{{{cond}}}")
        print(f"   Rolex {cond:<12} {(d or {}).get('total', 0):>8,}")

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=50,
                  aspect_filter=brand_filter("Rolex"))
    items = (d or {}).get("itemSummaries", []) or []
    with_img = sum(1 for i in items if i.get("image", {}).get("imageUrl"))
    with_thumbs = sum(1 for i in items if i.get("thumbnailImages"))
    conds = Counter(i.get("condition", "?") for i in items)

    print(f"\n   images in summary   {with_img}/{len(items)}")
    print(f"   thumbnail arrays    {with_thumbs}/{len(items)}")
    print(f"   condition labels seen: "
          f"{', '.join(f'{k}({v})' for k, v in conds.most_common())}")

    res["images_in_summary"] = f"{with_img}/{len(items)}"


# ------------------------------------------------------------------ main

TESTS = {"T1": t1_pagesize, "T2": t2_summary_fields, "T3": t3_fieldgroups,
         "T4": t4_composability, "T5": t5_deep_paging, "T6": t6_partition_leak,
         "T7": t7_title_parsing, "T8": t8_ratelimit_cost, "T9": t9_item_ids,
         "T10": t10_condition_images}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--marketplace", default="EBAY_GB")
    p.add_argument("--currency", default="GBP")
    p.add_argument("--test", nargs="*", default=list(TESTS))
    a = p.parse_args()

    OUT.mkdir(exist_ok=True)
    res = {"run_at": datetime.now(timezone.utc).isoformat(),
           "marketplace": a.marketplace, "currency": a.currency}

    print(f"\n  Round-three diagnostic  |  {a.marketplace} / {a.currency}")
    token()
    print("  auth ok")

    for t in [k for k in TESTS if k in a.test]:
        try:
            TESTS[t](a.marketplace, a.currency, res)
        except Exception as e:
            print(f"\n  {t} crashed: {type(e).__name__}: {e}")

    print(f"\n{'=' * 70}\n  CALLS USED: {sum(CALLS.values())}\n{'=' * 70}")
    for k, v in CALLS.most_common():
        print(f"   {v:>5}  {k}")

    res["calls"] = dict(CALLS)
    with open(OUT / "report3.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n  -> {OUT / 'report3.json'}\n")


if __name__ == "__main__":
    main()
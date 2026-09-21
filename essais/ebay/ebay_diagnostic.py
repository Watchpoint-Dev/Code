#!/usr/bin/env python3
"""
ebay_diagnostic.py — Full reconnaissance of eBay's watch data.

Answers, with evidence rather than guesswork:
  - Which API doors are open to my keyset, and which are locked?
  - How many calls do I actually have per day?
  - Which marketplace has the most watches?
  - Which brands dominate, and how deep does each go?
  - Which of the 45 aspects do sellers actually fill in?
  - How bad is reference-number keyword stuffing?
  - What does the price distribution look like?
  - How far can I paginate before eBay cuts me off?

Usage:
    python ebay_diagnostic.py                    # full run, ~150 calls
    python ebay_diagnostic.py --quick            # ~40 calls
    python ebay_diagnostic.py --sample 100       # deeper coverage sample
    python ebay_diagnostic.py --marketplace EBAY_DE
    python ebay_diagnostic.py --section coverage # run one section only

Outputs into ./diagnostic_output/ :
    report.json         everything, machine-readable
    aspects.csv         the full aspect list with metadata
    coverage.csv        fill rate per field, per brand
    items_sample.json   raw item detail for the sampled listings
"""

import argparse
import base64
import csv
import json
import os
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------- config

CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")

WRISTWATCH_CATEGORY = "31387"

MARKETPLACES = {
    "EBAY_GB": "United Kingdom",
    "EBAY_DE": "Germany",
    "EBAY_US": "United States",
    "EBAY_FR": "France",
    "EBAY_IT": "Italy",
    "EBAY_ES": "Spain",
}

# Brands worth profiling separately — coverage differs wildly by price tier.
PROBE_BRANDS = [
    "Rolex", "Omega", "Seiko", "Cartier", "Breitling",
    "Tudor", "TAG Heuer", "Casio", "Citizen", "Longines",
]

# Fields that actually matter for a watch database.
CRITICAL_FIELDS = [
    "Brand", "Model", "Reference Number", "Case Material", "Movement",
    "Case Size", "Year Manufactured", "Dial Colour", "Dial Color",
    "With Papers", "With Original Box/Packaging",
]

OUT = Path("diagnostic_output")

# ---------------------------------------------------------------- plumbing

class Calls:
    """Tracks API spend so you know what a run costs."""
    def __init__(self):
        self.n = 0
        self.by_endpoint = Counter()
        self.errors = []

    def hit(self, label):
        self.n += 1
        self.by_endpoint[label] += 1

    def error(self, label, status, body):
        self.errors.append({"endpoint": label, "status": status,
                            "body": str(body)[:300]})


CALLS = Calls()
_token = {"value": None, "expires": 0}


def die(msg):
    print(f"\n  FATAL: {msg}\n")
    sys.exit(1)


def get_token():
    if _token["value"] and time.time() < _token["expires"] - 60:
        return _token["value"]

    if not CLIENT_ID or not CLIENT_SECRET:
        die("EBAY_CLIENT_ID / EBAY_CLIENT_SECRET missing from .env")

    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={"Authorization": f"Basic {creds}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials",
              "scope": "https://api.ebay.com/oauth/api_scope"},
        timeout=30,
    )
    CALLS.hit("oauth/token")
    if r.status_code != 200:
        die(f"Auth failed [{r.status_code}]: {r.text[:400]}")

    d = r.json()
    _token["value"] = d["access_token"]
    _token["expires"] = time.time() + d.get("expires_in", 7200)
    return _token["value"]


def api(url, marketplace=None, label=None, **params):
    """GET with token. Returns (json_or_None, status_code)."""
    h = {"Authorization": f"Bearer {get_token()}"}
    if marketplace:
        h["X-EBAY-C-MARKETPLACE-ID"] = marketplace

    label = label or url.split("/")[-1]
    try:
        r = requests.get(url, headers=h, params=params or None, timeout=45)
    except requests.RequestException as e:
        CALLS.error(label, "NETWORK", e)
        return None, 0

    CALLS.hit(label)
    if r.status_code != 200:
        CALLS.error(label, r.status_code, r.text)
        return None, r.status_code
    try:
        return r.json(), 200
    except ValueError:
        return None, r.status_code


def head(title):
    print(f"\n{'=' * 68}\n  {title}\n{'=' * 68}")


def sub(title):
    print(f"\n  --- {title} ---")


def pct(part, whole):
    return 0.0 if not whole else round(part / whole * 100, 1)


# ---------------------------------------------------------------- sections

def section_access(report):
    """Which APIs will actually talk to you? This is the map of your options."""
    head("1. API ACCESS PROBE")
    print("  Testing which endpoints your keyset can reach.\n")

    probes = [
        ("Browse API (active listings)", "OPEN",
         "https://api.ebay.com/buy/browse/v1/item_summary/search",
         {"category_ids": WRISTWATCH_CATEGORY, "limit": 1}),
        ("Taxonomy API (category metadata)", "OPEN",
         "https://api.ebay.com/commerce/taxonomy/v1/get_default_category_tree_id",
         {"marketplace_id": "EBAY_GB"}),
        ("Developer Analytics (rate limits)", "OPEN",
         "https://api.ebay.com/developer/analytics/v1_beta/rate_limit/", {}),
        ("Marketplace Insights (SOLD data)", "GATED",
         "https://api.ebay.com/buy/marketplace_insights/v1_beta/item_sales/search",
         {"category_ids": WRISTWATCH_CATEGORY, "limit": 1}),
        ("Feed API (bulk download)", "GATED",
         "https://api.ebay.com/buy/feed/v1/access", {}),
    ]

    access = {}
    for name, expectation, url, params in probes:
        _, status = api(url, marketplace="EBAY_GB", label=name, **params)
        ok = status == 200
        access[name] = {"status": status, "accessible": ok,
                        "expected": expectation}
        mark = "OK  " if ok else "DENY"
        note = ""
        if not ok and status in (401, 403):
            note = "  <- limited release, requires eBay approval"
        elif not ok:
            note = f"  <- unexpected, check errors at end"
        print(f"   [{mark}] {status:<4} {name}{note}")

    if not access["Marketplace Insights (SOLD data)"]["accessible"]:
        print("\n   No sold-price access. Your only route to historical data is")
        print("   to snapshot active listings daily and detect disappearances.")

    report["access"] = access


def section_quota(report):
    """Your real daily budget, straight from eBay."""
    head("2. RATE LIMITS")

    data, status = api("https://api.ebay.com/developer/analytics/v1_beta/rate_limit/",
                       marketplace="EBAY_GB", label="rate_limit")
    if not data:
        print(f"  Could not read rate limits (status {status}).")
        print("  Assume the default 5,000 calls/day, application-wide.")
        report["rate_limits"] = {"error": status}
        return

    rows = []
    for grp in data.get("rateLimits", []):
        for res in grp.get("resources", []):
            for rate in res.get("rates", []):
                rows.append({
                    "api": grp.get("apiName"),
                    "resource": res.get("name"),
                    "limit": rate.get("limit"),
                    "remaining": rate.get("remaining"),
                    "reset": rate.get("reset"),
                })

    interesting = [r for r in rows if r["resource"] in
                   ("buy.browse", "buy.marketplace_insights", "buy.feed",
                    "commerce.taxonomy")]
    for r in (interesting or rows[:12]):
        used = (r["limit"] or 0) - (r["remaining"] or 0)
        print(f"   {r['resource']:<28} {used:>6} / {r['limit']:<8} used"
              f"   ({r['remaining']} left)")

    report["rate_limits"] = rows


def section_marketplaces(report, quick):
    """Where do the watches live? Sizes the opportunity per country."""
    head("3. MARKETPLACE COMPARISON")
    print("  Total active wristwatch listings per eBay site.\n")

    mkts = list(MARKETPLACES) if not quick else ["EBAY_GB", "EBAY_DE", "EBAY_US"]
    results = {}
    for mk in mkts:
        data, status = api(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            marketplace=mk, label=f"search[{mk}]",
            category_ids=WRISTWATCH_CATEGORY, limit=1)
        total = (data or {}).get("total", 0) if data else 0
        results[mk] = total
        flag = "" if data else f"  (status {status})"
        print(f"   {mk:<10} {MARKETPLACES[mk]:<16} {total:>10,} listings{flag}")

    if results:
        best = max(results, key=results.get)
        print(f"\n   Largest: {best} ({results[best]:,})")
        print("   Note: sites overlap little. Each is a separate crawl budget.")

    report["marketplaces"] = results


def section_aspects(report, marketplace):
    """The full field schema eBay offers, with which values are constrained."""
    head("4. ASPECT SCHEMA")

    tree, _ = api("https://api.ebay.com/commerce/taxonomy/v1/get_default_category_tree_id",
                  marketplace=marketplace, label="tree_id",
                  marketplace_id=marketplace)
    if not tree:
        print("  Could not fetch category tree.")
        return []

    tid = tree["categoryTreeId"]
    data, _ = api(
        f"https://api.ebay.com/commerce/taxonomy/v1/category_tree/{tid}"
        "/get_item_aspects_for_category",
        marketplace=marketplace, label="aspects",
        category_id=WRISTWATCH_CATEGORY)

    aspects = (data or {}).get("aspects", [])
    print(f"  {len(aspects)} aspects defined for category {WRISTWATCH_CATEGORY}\n")

    rows = []
    required = []
    for a in aspects:
        c = a.get("aspectConstraint", {})
        vals = a.get("aspectValues", [])
        row = {
            "name": a["localizedAspectName"],
            "required": c.get("aspectRequired", False),
            "data_type": c.get("aspectDataType", ""),
            "mode": c.get("aspectMode", ""),
            "cardinality": c.get("itemToAspectCardinality", ""),
            "allowed_values": len(vals),
            "sample_values": "; ".join(v["localizedValue"] for v in vals[:5]),
        }
        rows.append(row)
        if row["required"]:
            required.append(row["name"])

    print(f"  Required: {', '.join(required) or 'none'}")
    print(f"  Optional: {len(rows) - len(required)}")

    multi = [r["name"] for r in rows if r["cardinality"] == "MULTI"]
    print(f"\n  MULTI-value fields (can hold a list, and get abused for keyword")
    print(f"  stuffing): {len(multi)}")
    for m in multi[:12]:
        star = "  <-- watch this one" if "Reference" in m else ""
        print(f"     {m}{star}")

    OUT.mkdir(exist_ok=True)
    with open(OUT / "aspects.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  -> {OUT / 'aspects.csv'}")

    report["aspects"] = rows
    return rows


def section_brands(report, marketplace):
    """Brand distribution for free — one call, no per-item fetching."""
    head("5. BRAND DISTRIBUTION")
    print("  Using ASPECT_REFINEMENTS: eBay returns counts per brand in a")
    print("  single call. This is the cheapest census you can run.\n")

    data, status = api(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        marketplace=marketplace, label="search[refinements]",
        category_ids=WRISTWATCH_CATEGORY, limit=1,
        fieldgroups="ASPECT_REFINEMENTS")

    if not data:
        print(f"  Failed (status {status}).")
        return

    dist = {}
    for ad in data.get("refinement", {}).get("aspectDistributions", []):
        name = ad.get("localizedAspectName")
        vals = {v["localizedAspectValue"]: v["matchCount"]
                for v in ad.get("aspectValueDistributions", [])}
        dist[name] = vals

    brands = dist.get("Brand", {})
    if brands:
        total = sum(brands.values())
        print(f"  {len(brands)} brands, {total:,} listings covered\n")
        for b, c in sorted(brands.items(), key=lambda x: -x[1])[:25]:
            bar = "#" * int(c / max(brands.values()) * 34)
            print(f"   {b[:22]:<22} {c:>8,}  {bar}")
    else:
        print("  No brand refinement returned.")
        print("  Available refinements:", ", ".join(dist) or "none")

    report["brand_distribution"] = brands
    report["all_refinements"] = {k: len(v) for k, v in dist.items()}


def section_pagination(report, marketplace):
    """How deep can you actually page? Determines your partitioning strategy."""
    head("6. PAGINATION CEILING")
    print("  eBay caps how far you can page into one result set. Finding the")
    print("  wall tells you how finely you must slice your queries.\n")

    for offset in (0, 5000, 9800, 10000, 10200):
        data, status = api(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            marketplace=marketplace, label="search[paging]",
            category_ids=WRISTWATCH_CATEGORY, limit=1, offset=offset)
        got = len((data or {}).get("itemSummaries", []) or [])
        state = "ok" if got else f"blocked ({status})"
        print(f"   offset {offset:>6}  ->  {state}")

    print("\n   Practical ceiling is ~10,000 items per distinct query.")
    print("   To sweep the whole category you must partition by brand,")
    print("   then price band, then condition — until each slice is under it.")

    report["pagination_ceiling"] = 10000


def section_coverage(report, marketplace, sample, brands):
    """The heart of it: which fields do sellers actually fill in?"""
    head("7. FIELD COVERAGE + DATA QUALITY")
    print(f"  Sampling up to {sample} listings per brand and reading every")
    print(f"  aspect. This is the expensive part — 1 call per item.\n")

    per_brand = {}
    all_items = []
    global_counts = Counter()
    global_n = 0
    stuffing = defaultdict(lambda: {"stuffed": 0, "with_ref": 0, "total": 0})
    prices = defaultdict(list)
    sellers = Counter()

    for brand in brands:
        data, status = api(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            marketplace=marketplace, label="search[coverage]",
            category_ids=WRISTWATCH_CATEGORY, limit=min(sample, 200),
            aspect_filter=f"categoryId:{WRISTWATCH_CATEGORY},Brand:{{{brand}}}")

        summaries = (data or {}).get("itemSummaries", []) or []
        if not summaries:
            print(f"   {brand:<14} no results (status {status})")
            continue

        summaries = summaries[:sample]
        counts = Counter()
        n = 0

        for s in summaries:
            detail, st = api(
                f"https://api.ebay.com/buy/browse/v1/item/{s['itemId']}",
                marketplace=marketplace, label="getItem")
            if not detail:
                continue

            n += 1
            global_n += 1
            aspects = {a["name"]: a["value"]
                       for a in detail.get("localizedAspects", [])}

            for k in aspects:
                counts[k] += 1
                global_counts[k] += 1

            ref = aspects.get("Reference Number", "")
            stuffing[brand]["total"] += 1
            if ref:
                stuffing[brand]["with_ref"] += 1
                if ref.count(",") >= 2:
                    stuffing[brand]["stuffed"] += 1

            try:
                prices[brand].append(float(detail["price"]["value"]))
            except (KeyError, TypeError, ValueError):
                pass

            seller = (detail.get("seller") or {}).get("username")
            if seller:
                sellers[seller] += 1

            all_items.append({
                "itemId": s["itemId"],
                "title": detail.get("title"),
                "price": detail.get("price"),
                "brand_query": brand,
                "aspects": aspects,
            })

        per_brand[brand] = {"sampled": n, "counts": dict(counts)}
        crit = {f: pct(counts.get(f, 0), n) for f in CRITICAL_FIELDS
                if counts.get(f)}
        ref_rate = pct(stuffing[brand]["with_ref"], stuffing[brand]["total"])
        stuff_rate = pct(stuffing[brand]["stuffed"],
                         max(stuffing[brand]["with_ref"], 1))
        print(f"   {brand:<14} n={n:<4} ref#={ref_rate:>5.1f}%"
              f"   stuffed={stuff_rate:>5.1f}%")

    # global field fill rates
    sub(f"Field fill rate across all {global_n} sampled items")
    for field, c in global_counts.most_common(30):
        rate = pct(c, global_n)
        bar = "#" * int(rate / 3)
        star = " *" if field in CRITICAL_FIELDS else ""
        print(f"   {rate:>5.1f}%  {field[:30]:<30} {bar}{star}")

    sub("Critical fields")
    for f in CRITICAL_FIELDS:
        rate = pct(global_counts.get(f, 0), global_n)
        verdict = ("usable" if rate > 70 else
                   "patchy" if rate > 35 else "unreliable")
        print(f"   {rate:>5.1f}%  {f:<32} {verdict}")

    sub("Reference number quality")
    tot = sum(v["total"] for v in stuffing.values())
    wref = sum(v["with_ref"] for v in stuffing.values())
    stf = sum(v["stuffed"] for v in stuffing.values())
    print(f"   have a reference number : {pct(wref, tot)}%")
    print(f"   of those, keyword-stuffed: {pct(stf, max(wref,1))}%")
    print(f"   clean + usable overall   : {pct(wref - stf, tot)}%")
    print("\n   'Stuffed' = 3+ comma-separated values, i.e. a seller listing")
    print("   every reference they hope to rank for. These need filtering or")
    print("   cross-checking against the title before you trust them.")

    sub("Price distribution")
    for brand, vals in prices.items():
        if len(vals) < 3:
            continue
        vals.sort()
        print(f"   {brand:<14} n={len(vals):<4} "
              f"min={vals[0]:>9,.0f}  med={statistics.median(vals):>9,.0f}  "
              f"max={vals[-1]:>10,.0f}")

    sub("Seller concentration")
    print(f"   {len(sellers)} distinct sellers across {global_n} listings")
    for s, c in sellers.most_common(8):
        print(f"   {c:>4} listings  {s}")
    if sellers:
        top = sum(c for _, c in sellers.most_common(10))
        print(f"\n   Top 10 sellers hold {pct(top, global_n)}% of sampled stock.")

    OUT.mkdir(exist_ok=True)
    with open(OUT / "coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "count", "sampled", "fill_rate_pct", "critical"])
        for field, c in global_counts.most_common():
            w.writerow([field, c, global_n, pct(c, global_n),
                        field in CRITICAL_FIELDS])

    with open(OUT / "items_sample.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"\n  -> {OUT / 'coverage.csv'}")
    print(f"  -> {OUT / 'items_sample.json'}  ({len(all_items)} items)")

    report["coverage"] = {
        "sampled": global_n,
        "field_counts": dict(global_counts),
        "fill_rates": {k: pct(v, global_n) for k, v in global_counts.items()},
        "per_brand": per_brand,
        "reference_quality": {
            "total": tot, "with_ref": wref, "stuffed": stf,
            "clean_pct": pct(wref - stf, tot),
        },
        "seller_concentration": dict(sellers.most_common(50)),
    }


def section_plan(report):
    """Turn the measurements into a crawl budget."""
    head("8. CRAWL FEASIBILITY")

    brands = report.get("brand_distribution", {})
    total = sum(brands.values()) if brands else 0
    if not total:
        print("  No brand data; skipping.")
        return

    daily = 5000
    print(f"  Category size (this marketplace): {total:,} listings")
    print(f"  Assumed daily quota:              {daily:,} calls\n")

    search_calls = -(-total // 200)          # 200 per page, ceil
    detail_calls = total                      # 1 per item for aspects
    print(f"  Search-only sweep (summaries):    {search_calls:,} calls"
          f"  = {search_calls/daily:.1f} days")
    print(f"  Full sweep with item details:     {detail_calls:,} calls"
          f"  = {detail_calls/daily:.1f} days")

    print("\n  Reality check: a full detailed sweep of every watch is not")
    print("  feasible at 5,000/day. Three ways forward:\n")
    print("   1. Narrow the scope. Top 5 brands only:")
    top5 = sorted(brands.items(), key=lambda x: -x[1])[:5]
    n5 = sum(c for _, c in top5)
    print(f"      {', '.join(b for b, _ in top5)}")
    print(f"      {n5:,} listings = {n5/daily:.1f} days per full pass")
    print("   2. Search-only snapshots daily (cheap), item details only for")
    print("      new listings you haven't seen before.")
    print("   3. Apply for the Feed API — bulk TSV, no per-item calls.")

    report["crawl_plan"] = {
        "category_total": total,
        "search_calls": search_calls,
        "detail_calls": detail_calls,
        "top5": dict(top5),
    }


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--marketplace", default="EBAY_GB", choices=list(MARKETPLACES))
    p.add_argument("--sample", type=int, default=15,
                   help="listings sampled per brand for coverage (default 15)")
    p.add_argument("--quick", action="store_true", help="fewer brands, fewer sites")
    p.add_argument("--section", default="all",
                   choices=["all", "access", "quota", "marketplaces", "aspects",
                            "brands", "pagination", "coverage", "plan"])
    args = p.parse_args()

    brands = PROBE_BRANDS[:3] if args.quick else PROBE_BRANDS[:6]
    sample = 5 if args.quick else args.sample

    OUT.mkdir(exist_ok=True)
    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "marketplace": args.marketplace,
        "sample_per_brand": sample,
    }

    print(f"\n  eBay watch data diagnostic")
    print(f"  marketplace={args.marketplace}  sample={sample}/brand"
          f"  brands={len(brands)}")

    get_token()
    print("  auth ok")

    S = args.section
    if S in ("all", "access"):       section_access(report)
    if S in ("all", "quota"):        section_quota(report)
    if S in ("all", "marketplaces"): section_marketplaces(report, args.quick)
    if S in ("all", "aspects"):      section_aspects(report, args.marketplace)
    if S in ("all", "brands"):       section_brands(report, args.marketplace)
    if S in ("all", "pagination"):   section_pagination(report, args.marketplace)
    if S in ("all", "coverage"):     section_coverage(report, args.marketplace,
                                                      sample, brands)
    if S in ("all", "plan"):         section_plan(report)

    head("RUN SUMMARY")
    print(f"  API calls used: {CALLS.n}")
    for ep, c in CALLS.by_endpoint.most_common(10):
        print(f"     {c:>5}  {ep}")

    if CALLS.errors:
        print(f"\n  Errors ({len(CALLS.errors)}):")
        seen = set()
        for e in CALLS.errors:
            key = (e["endpoint"], e["status"])
            if key in seen:
                continue
            seen.add(key)
            print(f"     [{e['status']}] {e['endpoint']}")
            print(f"           {e['body'][:160]}")

    report["calls_used"] = CALLS.n
    report["errors"] = CALLS.errors

    with open(OUT / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  -> {OUT / 'report.json'}")
    print(f"\n  Done.\n")


if __name__ == "__main__":
    main()
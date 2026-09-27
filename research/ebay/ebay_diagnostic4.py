#!/usr/bin/env python3
"""
ebay_diagnostic4.py — The big one. Everything that still matters.

Fixes two broken tests from round three and adds a real end-to-end sweep
that either proves the crawler design or kills it.

  FIXES
  F1   Pagination ceiling      binary search for the actual wall
  F2   Rate limit accounting   proper N=100 measurement with settle time
  F3   Price partitioning      non-overlapping bands + boundary proof
  F4   Reference regex         year-excluding, brand-aware patterns

  NEW
  N1   FULL SWEEP PROOF        retrieve an entire brand, reconcile counts
  N2   Sort reachability       can sorting extend past the ceiling?
  N3   Result stability        same query twice — how much drifts?
  N4   Currency mix            what is actually on EBAY_GB?
  N5   epid coverage           is there a real catalog join key?
  N6   Listing age             lifespan estimate for disappearance logic
  N7   Partition dimensions    cardinality of condition/format/model
  N8   Record size             storage projection
  N9   Error behaviour         404s, bad IDs, malformed filters
  N10  Seller landscape        concentration in the luxury tier

Usage:
    python ebay_diagnostic4.py                 # ~600 calls, 15 min
    python ebay_diagnostic4.py --light         # ~200 calls
    python ebay_diagnostic4.py --test F3 N1
    python ebay_diagnostic4.py --sweep-brand TUDOR
"""

import argparse
import base64
import json
import os
import re
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

B = "https://api.ebay.com/buy/browse/v1"
SEARCH = f"{B}/item_summary/search"
ITEM = f"{B}/item"
RL = "https://api.ebay.com/developer/analytics/v1_beta/rate_limit/"

CALLS = Counter()
_tok = {"v": None, "exp": 0}


def token():
    if _tok["v"] and time.time() < _tok["exp"] - 60:
        return _tok["v"]
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
    _tok["v"], _tok["exp"] = d["access_token"], time.time() + d.get("expires_in", 7200)
    return _tok["v"]


def get(url, mk, label, retries=2, **params):
    h = {"Authorization": f"Bearer {token()}", "X-EBAY-C-MARKETPLACE-ID": mk}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=h, params=params or None, timeout=60)
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None, 0, str(e)
        CALLS[label] += 1
        if r.status_code == 429:
            time.sleep(3)
            continue
        if r.status_code != 200:
            return None, r.status_code, r.text[:400]
        try:
            return r.json(), 200, None
        except ValueError:
            return None, r.status_code, "bad json"
    return None, 0, "retries exhausted"


def bf(brand):
    return f"categoryId:{CAT},Brand:{{{brand}}}"


def head(tag, title):
    print(f"\n{'=' * 72}\n  {tag}. {title}\n{'=' * 72}")


def total_for(mk, **params):
    d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1, **params)
    return (d or {}).get("total", 0) if st == 200 else None


# ================================================================== F1

def f1_ceiling(mk, cur, res, light):
    head("F1", "PAGINATION CEILING — binary search for the real wall")
    print("  Round one said blocked at 10,000. Round three said 10,000 worked.")
    print("  Finding the truth by bisection.\n")

    def works(offset):
        d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                       offset=offset, aspect_filter=bf("Rolex"))
        return st == 200 and len((d or {}).get("itemSummaries", []) or []) > 0

    lo, hi = 0, 20000
    if not works(lo):
        print("   offset 0 failed — aborting.")
        return

    # expand until failure
    probe = 1000
    while probe <= 40000 and works(probe):
        print(f"   offset {probe:>6}  ok")
        lo = probe
        probe *= 2
    hi = probe
    print(f"   offset {hi:>6}  blocked")

    while hi - lo > 50:
        mid = (lo + hi) // 2
        if works(mid):
            lo = mid
        else:
            hi = mid
    print(f"\n   Actual ceiling: between {lo:,} and {hi:,}")
    print(f"   Design against {lo:,} reachable items per query.")
    res["ceiling"] = {"last_ok": lo, "first_blocked": hi}


# ================================================================== F2

def f2_ratelimit(mk, cur, res, light):
    head("F2", "RATE LIMIT ACCOUNTING — done properly this time")
    print("  Round three used N=5 and got noise. Using N=100 with settle.\n")

    def remaining():
        d, _, _ = get(RL, mk, "ratelimit")
        for g in (d or {}).get("rateLimits", []):
            for r_ in g.get("resources", []):
                if r_.get("name") == "buy.browse":
                    for rate in r_.get("rates", []):
                        return rate.get("remaining")
        return None

    before = remaining()
    if before is None:
        print("   Could not read quota.")
        return

    N = 30 if light else 100
    print(f"   before: {before:,}   making {N} calls...")
    t0 = time.time()
    for i in range(N):
        get(SEARCH, mk, "search", category_ids=CAT, limit=1, offset=i)
    dur = time.time() - t0

    print(f"   done in {dur:.1f}s, waiting 20s for counters to settle...")
    time.sleep(20)
    after = remaining()

    used = before - after
    ratio = used / N
    print(f"   after:  {after:,}")
    print(f"   consumed {used} for {N} calls  ->  {ratio:.2f} per request")
    print(f"   throughput: {N/dur:.1f} calls/sec")
    verdict = ("1:1 as assumed" if 0.9 <= ratio <= 1.15 else
               f"NOT 1:1 — budget is {5000/max(ratio,0.01):,.0f} effective calls/day")
    print(f"   -> {verdict}")
    res["ratelimit"] = {"before": before, "after": after, "n": N,
                        "consumed": used, "ratio": round(ratio, 3),
                        "calls_per_sec": round(N / dur, 2)}


# ================================================================== F3

def f3_partition(mk, cur, res, light):
    head("F3", "PRICE PARTITIONING — non-overlapping bands + boundary proof")
    print("  Round three overcounted OMEGA by 51%. Testing whether eBay's")
    print("  range bounds are inclusive on both ends.\n")

    # --- boundary proof: does an item at exactly X appear in both bands?
    print("   Boundary test on Rolex:")
    a = total_for(mk, aspect_filter=bf("Rolex"),
                  filter=f"price:[1000..2000],priceCurrency:{cur}")
    b = total_for(mk, aspect_filter=bf("Rolex"),
                  filter=f"price:[2000..3000],priceCurrency:{cur}")
    wide = total_for(mk, aspect_filter=bf("Rolex"),
                     filter=f"price:[1000..3000],priceCurrency:{cur}")
    a2 = total_for(mk, aspect_filter=bf("Rolex"),
                   filter=f"price:[1000..1999],priceCurrency:{cur}")
    b2 = total_for(mk, aspect_filter=bf("Rolex"),
                   filter=f"price:[2000..2999],priceCurrency:{cur}")
    wide2 = total_for(mk, aspect_filter=bf("Rolex"),
                      filter=f"price:[1000..2999],priceCurrency:{cur}")

    print(f"      [1000..2000] + [2000..3000] = {(a or 0)+(b or 0):,}"
          f"   vs [1000..3000] = {wide:,}")
    print(f"      overlap at boundary: {(a or 0)+(b or 0)-(wide or 0):,}")
    print(f"      [1000..1999] + [2000..2999] = {(a2 or 0)+(b2 or 0):,}"
          f"   vs [1000..2999] = {wide2:,}")
    print(f"      overlap: {(a2 or 0)+(b2 or 0)-(wide2 or 0):,}")

    # --- reconciliation with clean integer bands
    edges = [0, 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000,
             10000, 15000, 20000, 30000, 50000, 100000]
    brands = ["Rolex", "OMEGA"] if not light else ["Rolex"]

    for brand in brands:
        print(f"\n   {brand} — clean non-overlapping bands:")
        total = total_for(mk, aspect_filter=bf(brand))
        summed = 0
        over = []
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1] - 1
            n = total_for(mk, aspect_filter=bf(brand),
                          filter=f"price:[{lo}..{hi}],priceCurrency:{cur}")
            summed += n or 0
            if n and n > 9000:
                over.append((lo, hi, n))
        tail = total_for(mk, aspect_filter=bf(brand),
                         filter=f"price:[{edges[-1]}],priceCurrency:{cur}")
        summed += tail or 0

        leak = (total or 0) - summed
        print(f"      brand total   {total:>8,}")
        print(f"      band sum      {summed:>8,}")
        print(f"      leak          {leak:>8,}  ({leak/max(total,1)*100:+.2f}%)")
        if over:
            print(f"      bands still over 9k: "
                  f"{', '.join(f'{l}-{h}({n:,})' for l, h, n in over)}")

        # where does the leak live? probe non-price listings
        auc = total_for(mk, aspect_filter=bf(brand),
                        filter="buyingOptions:{AUCTION}")
        print(f"      auctions in brand: {auc:,}"
              f"  (candidates for price-less listings)")

        res.setdefault("partition", {})[brand] = {
            "total": total, "summed": summed, "leak": leak,
            "over_bands": over}


# ================================================================== F4

YEAR = re.compile(r"^(19|20)\d{2}$")

REF_PATTERNS = [
    # Omega style: 123.45.67.89.01.001 / 1502.30.00
    (r"\b(\d{3,4}\.\d{2}\.\d{2}(?:\.\d{2}){0,3})\b", "dotted"),
    # TAG style: CAZ1014.BA0842
    (r"\b([A-Z]{2,4}\d{3,4}\.[A-Z]{2}\d{4})\b", "alpha-dot"),
    # Seiko style: 7S26-0020, 7N32-0AM0
    (r"\b(\d[A-Z]\d{2}-\d[A-Z0-9]{3})\b", "seiko"),
    # Rolex style with suffix: 116610LN, 126713GRNR
    (r"\b(\d{4,6}[A-Z]{2,4})\b", "num+suffix"),
    # bare 5-6 digit (Rolex modern), never a year
    (r"\b(\d{5,6})\b", "bare5-6"),
    # ref-prefixed
    (r"(?:ref|reference)[\s.:#]*([A-Z0-9][A-Z0-9./-]{3,})", "ref-prefix"),
    # bare 4-digit, only if not a year
    (r"\b(\d{4})\b", "bare4"),
]


def extract_ref(title):
    t = title.upper()
    for pat, name in REF_PATTERNS:
        for m in re.finditer(pat, t, re.IGNORECASE):
            cand = m.group(1)
            if YEAR.match(cand):
                continue
            if cand.isdigit() and len(cand) == 4 and cand.startswith(("19", "20")):
                continue
            return cand, name
    return None, None


def f4_regex(mk, cur, res, light):
    head("F4", "REFERENCE REGEX — year-excluded, brand-aware")
    print("  Round three scored 77%; every failure was a year. Retesting.\n")

    brands = ["Rolex", "OMEGA", "TAG Heuer"] if not light else ["Rolex"]
    n_per = 20 if light else 40
    agg = Counter()
    misses = []
    pattern_use = Counter()

    for brand in brands:
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=n_per,
                      aspect_filter=bf(brand))
        rows = [(i["itemId"], i.get("title", ""))
                for i in (d or {}).get("itemSummaries", [])]

        both = ok = bad = titleonly = 0
        for iid, title in rows:
            det, st, _ = get(f"{ITEM}/{iid}", mk, "getItem")
            if not det:
                continue
            asp = {a["name"]: a["value"]
                   for a in det.get("localizedAspects", []) or []}
            true = asp.get("Reference Number")
            guess, pat = extract_ref(title)
            if pat:
                pattern_use[pat] += 1

            if true and guess:
                both += 1
                t = true.upper().replace(" ", "")
                g = guess.upper().replace(" ", "")
                if g in t or t in g or any(g == p.strip() for p in t.split(",")):
                    ok += 1
                else:
                    bad += 1
                    if len(misses) < 10:
                        misses.append((brand, title[:50], true[:22], guess))
            elif guess and not true:
                titleonly += 1

        rate = ok / max(both, 1) * 100
        print(f"   {brand:<12} n={len(rows):<3} matched={both:<3}"
              f" correct={ok:<3} ({rate:.0f}%)  title-only gain={titleonly}")
        agg["both"] += both
        agg["ok"] += ok
        agg["bad"] += bad
        agg["titleonly"] += titleonly

    print(f"\n   OVERALL accuracy: {agg['ok']}/{agg['both']}"
          f" = {agg['ok']/max(agg['both'],1)*100:.1f}%"
          f"   (round three: 77%)")
    print(f"   extra refs recovered from titles: {agg['titleonly']}")
    print(f"\n   pattern usage: "
          f"{', '.join(f'{k}={v}' for k, v in pattern_use.most_common())}")
    if misses:
        print("\n   Remaining failures:")
        for b_, t_, tr, g_ in misses[:8]:
            print(f"      [{b_}] {t_}")
            print(f"         aspect={tr}  regex={g_}")

    res["regex"] = dict(agg)


# ================================================================== N1

def n1_full_sweep(mk, cur, res, light, brand="TUDOR"):
    head("N1", f"FULL SWEEP PROOF — retrieve every {brand} listing")
    print("  This is the real test. If a complete brand cannot be")
    print("  retrieved and reconciled, the crawler design is wrong.\n")

    reported = total_for(mk, aspect_filter=bf(brand))
    if not reported:
        print(f"   No listings for {brand}.")
        return
    print(f"   Reported total: {reported:,}\n")

    edges = [0, 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7000,
             10000, 15000, 25000, 50000]
    seen = set()
    dupes = 0
    band_stats = []
    calls_before = sum(CALLS.values())

    slices = [(edges[i], edges[i + 1] - 1) for i in range(len(edges) - 1)]
    slices.append((edges[-1], None))

    for lo, hi in slices:
        rng = f"[{lo}..{hi}]" if hi else f"[{lo}]"
        flt = f"price:{rng},priceCurrency:{cur}"
        band_total = total_for(mk, aspect_filter=bf(brand), filter=flt)
        if not band_total:
            continue

        got = 0
        offset = 0
        while offset < min(band_total, 10000):
            d, st, err = get(SEARCH, mk, "search", category_ids=CAT,
                             limit=200, offset=offset,
                             aspect_filter=bf(brand), filter=flt)
            if st != 200:
                print(f"      band {lo}-{hi} offset {offset} failed: {st}")
                break
            items = (d or {}).get("itemSummaries", []) or []
            if not items:
                break
            for i in items:
                iid = i["itemId"]
                if iid in seen:
                    dupes += 1
                seen.add(iid)
            got += len(items)
            offset += 200
            if len(items) < 200:
                break

        band_stats.append((lo, hi, band_total, got))
        label = f"{lo}-{hi}" if hi else f"{lo}+"
        flag = "  INCOMPLETE" if got < min(band_total, 10000) else ""
        print(f"      {label:<12} reported={band_total:>6,}"
              f"  retrieved={got:>6,}{flag}")

    # sweep listings with no price constraint at all, to catch the leak
    print("\n   Probing for listings missed by price bands...")
    extra = 0
    for extra_filter in ("buyingOptions:{AUCTION}",
                         "conditions:{NEW}",
                         "conditions:{USED}"):
        offset = 0
        while offset < 2000:
            d, st, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=200,
                           offset=offset, aspect_filter=bf(brand),
                           filter=extra_filter)
            items = (d or {}).get("itemSummaries", []) or []
            if not items:
                break
            for i in items:
                if i["itemId"] not in seen:
                    extra += 1
                    seen.add(i["itemId"])
            offset += 200
            if len(items) < 200:
                break

    calls_used = sum(CALLS.values()) - calls_before
    unique = len(seen)
    cov = unique / reported * 100

    print(f"\n   RESULT")
    print(f"      reported total     {reported:>8,}")
    print(f"      unique retrieved   {unique:>8,}")
    print(f"      coverage           {cov:>7.1f}%")
    print(f"      cross-band dupes   {dupes:>8,}")
    print(f"      recovered by extra {extra:>8,}")
    print(f"      calls used         {calls_used:>8,}")
    print(f"      calls per 1k items {calls_used/max(unique,1)*1000:>8.1f}")

    proj = 182177 / max(unique, 1) * calls_used
    print(f"\n      Projected full luxury sweep: {proj:,.0f} calls"
          f"  ({proj/5000*100:.0f}% of daily budget)")

    if cov >= 95:
        print("      -> design VALIDATED")
    elif cov >= 80:
        print("      -> workable but leaky; add overflow slices")
    else:
        print("      -> design FAILS; partitioning cannot reach the data")

    res["sweep"] = {"brand": brand, "reported": reported, "unique": unique,
                    "coverage_pct": round(cov, 2), "dupes": dupes,
                    "extra": extra, "calls": calls_used,
                    "projected_luxury_calls": int(proj)}
    res["_sweep_ids"] = list(seen)[:5000]


# ================================================================== N2

def n2_sort_reach(mk, cur, res, light):
    head("N2", "SORT REACHABILITY — can sorting beat the ceiling?")
    print("  If ascending and descending reach different items, sorting")
    print("  both ways doubles what you can pull from one query.\n")

    sorts = ["price", "-price", "newlyListed", "endingSoonest", None]
    sets = {}
    for s in sorts:
        p = {"aspect_filter": bf("Rolex"), "limit": 200}
        if s:
            p["sort"] = s
        d, st, err = get(SEARCH, mk, "search", category_ids=CAT, **p)
        if st != 200:
            print(f"   sort={str(s):<14} FAIL {st}  {(err or '')[:60]}")
            continue
        ids = {i["itemId"] for i in (d or {}).get("itemSummaries", []) or []}
        sets[str(s)] = ids
        print(f"   sort={str(s):<14} ok   {len(ids)} items")

    keys = list(sets)
    if len(keys) >= 2:
        print("\n   Overlap between sort orders (first 200 each):")
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b_ = sets[keys[i]], sets[keys[j]]
                ov = len(a & b_)
                print(f"      {keys[i]:<14} vs {keys[j]:<14} "
                      f"shared {ov:>3}/{len(a)}")
        union = set().union(*sets.values())
        print(f"\n   union of all sorts: {len(union)} unique"
              f" vs {max(len(s) for s in sets.values())} from one")


# ================================================================== N3

def n3_stability(mk, cur, res, light):
    head("N3", "RESULT STABILITY — same query twice")
    print("  Tells you how much drift to expect between crawl passes.\n")

    p = dict(aspect_filter=bf("Rolex"), limit=200, sort="newlyListed")
    d1, _, _ = get(SEARCH, mk, "search", category_ids=CAT, **p)
    ids1 = [i["itemId"] for i in (d1 or {}).get("itemSummaries", []) or []]
    t1 = (d1 or {}).get("total", 0)

    time.sleep(3)
    d2, _, _ = get(SEARCH, mk, "search", category_ids=CAT, **p)
    ids2 = [i["itemId"] for i in (d2 or {}).get("itemSummaries", []) or []]
    t2 = (d2 or {}).get("total", 0)

    s1, s2 = set(ids1), set(ids2)
    print(f"   run 1: {len(ids1)} items, total={t1:,}")
    print(f"   run 2: {len(ids2)} items, total={t2:,}")
    print(f"   identical order: {ids1 == ids2}")
    print(f"   set difference:  {len(s1 ^ s2)} items")
    print(f"   total drift:     {t2 - t1:+,}")
    if s1 ^ s2:
        print("\n   Results shift between calls. Paginating a large set is")
        print("   not a consistent snapshot — expect small gaps and dupes.")

    res["stability"] = {"diff": len(s1 ^ s2), "same_order": ids1 == ids2,
                        "total_drift": t2 - t1}


# ================================================================== N4

def n4_currency(mk, cur, res, light):
    head("N4", "CURRENCY MIX — what is actually on this marketplace?")
    print("  Likely explanation for the partition leak.\n")

    for c in ("GBP", "USD", "EUR", "CHF", "AUD", "CAD"):
        n = total_for(mk, aspect_filter=bf("Rolex"),
                      filter=f"price:[0..1000000],priceCurrency:{c}")
        print(f"   Rolex priced in {c}: {n:>8,}" if n is not None
              else f"   Rolex priced in {c}: n/a")

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=200,
                  aspect_filter=bf("Rolex"))
    cs = Counter(i.get("price", {}).get("currency", "?")
                 for i in (d or {}).get("itemSummaries", []) or [])
    print(f"\n   Currencies in a live 200-item sample: "
          f"{', '.join(f'{k}={v}' for k, v in cs.most_common())}")

    noprice = sum(1 for i in (d or {}).get("itemSummaries", []) or []
                  if not i.get("price", {}).get("value"))
    print(f"   items with no price value: {noprice}")
    res["currencies"] = dict(cs)


# ================================================================== N5

def n5_epid(mk, cur, res, light):
    head("N5", "EPID COVERAGE — is there a catalog join key?")
    print("  epid is eBay's own product ID. Where present it beats every")
    print("  string field for grouping identical watches.\n")

    for brand in (["Rolex", "OMEGA", "Seiko"] if not light else ["Rolex"]):
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=200,
                      aspect_filter=bf(brand))
        items = (d or {}).get("itemSummaries", []) or []
        with_epid = [i for i in items if i.get("epid")]
        uniq = len({i["epid"] for i in with_epid})
        print(f"   {brand:<10} {len(with_epid):>3}/{len(items)} have epid"
              f"  ({len(with_epid)/max(len(items),1)*100:.0f}%)"
              f"   {uniq} distinct products")
        if with_epid:
            top = Counter(i["epid"] for i in with_epid).most_common(2)
            print(f"      most common epid: {top}")


# ================================================================== N6

def n6_age(mk, cur, res, light):
    head("N6", "LISTING AGE — lifespan estimate for disappearance logic")
    print("  How long does a listing stay up? Sets the crawl cadence.\n")

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=200,
                  aspect_filter=bf("Rolex"))
    now = datetime.now(timezone.utc)
    ages = []
    for i in (d or {}).get("itemSummaries", []) or []:
        cd = i.get("itemCreationDate")
        if not cd:
            continue
        try:
            dt = datetime.fromisoformat(cd.replace("Z", "+00:00"))
            ages.append((now - dt).days)
        except ValueError:
            pass

    if not ages:
        print("   No creation dates.")
        return

    ages.sort()
    buckets = [(0, 1, "today"), (1, 7, "1-7d"), (7, 30, "1-4w"),
               (30, 90, "1-3m"), (90, 365, "3-12m"), (365, 99999, "1y+")]
    print(f"   sampled {len(ages)} active listings\n")
    for lo, hi, name in buckets:
        c = sum(1 for a in ages if lo <= a < hi)
        bar = "#" * int(c / len(ages) * 40)
        print(f"      {name:<8} {c:>4} ({c/len(ages)*100:>5.1f}%)  {bar}")

    print(f"\n   median age: {statistics.median(ages):.0f} days")
    print(f"   mean age:   {statistics.mean(ages):.0f} days")
    old = sum(1 for a in ages if a > 90)
    print(f"   older than 90d: {old} ({old/len(ages)*100:.0f}%)")
    print("\n   High median age = listings sit unsold for a long time,")
    print("   so disappearance is a weak sale signal and daily crawling")
    print("   of unchanged items is mostly wasted budget.")

    res["age"] = {"median_days": statistics.median(ages),
                  "mean_days": round(statistics.mean(ages), 1),
                  "over_90d_pct": round(old / len(ages) * 100, 1)}


# ================================================================== N7

def n7_dimensions(mk, cur, res, light):
    head("N7", "PARTITION DIMENSIONS — what else can split a big slice?")
    print("  When a price band exceeds the ceiling, you need another axis.\n")

    base = total_for(mk, aspect_filter=bf("Rolex"))
    print(f"   Rolex total: {base:,}\n")

    print("   By condition:")
    for c in ("NEW", "USED", "UNSPECIFIED"):
        n = total_for(mk, aspect_filter=bf("Rolex"), filter=f"conditions:{{{c}}}")
        print(f"      {c:<14} {n:>8,}")

    print("\n   By buying option:")
    for o in ("FIXED_PRICE", "AUCTION", "BEST_OFFER"):
        n = total_for(mk, aspect_filter=bf("Rolex"),
                      filter=f"buyingOptions:{{{o}}}")
        print(f"      {o:<14} {n:>8,}")

    print("\n   By model (top values from refinements):")
    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=1,
                  aspect_filter=bf("Rolex"), fieldgroups="ASPECT_REFINEMENTS")
    models = {}
    for ad in (d or {}).get("refinement", {}).get("aspectDistributions", []):
        if ad.get("localizedAspectName") == "Model":
            models = {v["localizedAspectValue"]: v["matchCount"]
                      for v in ad.get("aspectValueDistributions", [])}
    for m, c in sorted(models.items(), key=lambda x: -x[1])[:12]:
        print(f"      {m[:34]:<34} {c:>8,}")
    print(f"\n      {len(models)} distinct Rolex models available as a filter")

    print("\n   By seller location:")
    for loc in ("GB", "US", "DE", "CH", "IT"):
        n = total_for(mk, aspect_filter=bf("Rolex"),
                      filter=f"itemLocationCountry:{loc}")
        print(f"      {loc:<14} {n:>8,}")

    res["dimensions"] = {"models": len(models)}


# ================================================================== N8

def n8_size(mk, cur, res, light):
    head("N8", "RECORD SIZE — storage projection")
    print()

    d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=10,
                  aspect_filter=bf("Rolex"))
    items = (d or {}).get("itemSummaries", []) or []
    if not items:
        return
    sm = statistics.mean(len(json.dumps(i)) for i in items)

    details = []
    for i in items[:3]:
        det, st, _ = get(f"{ITEM}/{i['itemId']}", mk, "getItem")
        if det:
            details.append(det)
    dt = statistics.mean(len(json.dumps(x)) for x in details) if details else 0
    dt_nodesc = 0
    if details:
        stripped = [{k: v for k, v in x.items()
                     if k not in ("description", "shortDescription")}
                    for x in details]
        dt_nodesc = statistics.mean(len(json.dumps(x)) for x in stripped)

    print(f"   avg summary record:        {sm:>9,.0f} bytes")
    print(f"   avg full detail record:    {dt:>9,.0f} bytes")
    print(f"   detail without description:{dt_nodesc:>9,.0f} bytes")

    pool = 182177
    print(f"\n   Luxury pool ({pool:,} listings):")
    print(f"      summaries only:      {pool*sm/1e9:>8.2f} GB")
    print(f"      + details (no desc): {pool*(sm+dt_nodesc)/1e9:>8.2f} GB")
    print(f"      + full details:      {pool*(sm+dt)/1e9:>8.2f} GB")
    print(f"\n   One daily snapshot per listing for a year:")
    print(f"      {pool*sm*365/1e9:>8.1f} GB raw"
          f"  (far less if you only store changed fields)")

    res["sizes"] = {"summary_bytes": int(sm), "detail_bytes": int(dt),
                    "detail_nodesc_bytes": int(dt_nodesc)}


# ================================================================== N9

def n9_errors(mk, cur, res, light):
    head("N9", "ERROR BEHAVIOUR — what breaks, and how loudly?")
    print("  Silent failures are the dangerous kind. Round one found eBay")
    print("  silently ignoring a bad brand filter.\n")

    cases = [
        ("nonexistent item id", f"{ITEM}/v1|999999999999|0", {}),
        ("malformed item id", f"{ITEM}/not-an-id", {}),
        ("bogus brand value", SEARCH,
         {"category_ids": CAT, "limit": 1,
          "aspect_filter": f"categoryId:{CAT},Brand:{{ZZZNotARealBrand}}"}),
        ("bogus aspect name", SEARCH,
         {"category_ids": CAT, "limit": 1,
          "aspect_filter": f"categoryId:{CAT},NotAnAspect:{{Foo}}"}),
        ("invalid category", SEARCH, {"category_ids": "99999999", "limit": 1}),
        ("malformed price filter", SEARCH,
         {"category_ids": CAT, "limit": 1, "filter": "price:[abc..def]"}),
        ("negative offset", SEARCH,
         {"category_ids": CAT, "limit": 1, "offset": -5}),
        ("bad currency code", SEARCH,
         {"category_ids": CAT, "limit": 1,
          "filter": "price:[0..100],priceCurrency:XXX"}),
    ]

    baseline = total_for(mk, category_ids=CAT) if False else total_for(mk)
    for name, url, params in cases:
        d, st, err = get(url, mk, "errtest", retries=0, **params)
        total = (d or {}).get("total") if d else None
        if st == 200:
            silent = (total is not None and baseline
                      and abs(total - baseline) / max(baseline, 1) < 0.02)
            tag = "  <-- SILENT PASS-THROUGH, DANGEROUS" if silent else ""
            print(f"   {name:<24} 200  total={total}{tag}")
        else:
            code = ""
            try:
                code = json.loads(err).get("errors", [{}])[0].get("errorId", "")
            except Exception:
                pass
            print(f"   {name:<24} {st}  errorId={code}")

    print("\n   Any 'SILENT PASS-THROUGH' above means eBay ignored your")
    print("   filter and returned everything. The crawler must verify")
    print("   returned data matches what it asked for.")


# ================================================================== N10

def n10_sellers(mk, cur, res, light):
    head("N10", "SELLER LANDSCAPE — concentration in luxury")
    print()

    sellers = Counter()
    feedback = {}
    for brand in (["Rolex", "OMEGA", "TAG Heuer"] if not light else ["Rolex"]):
        d, _, _ = get(SEARCH, mk, "search", category_ids=CAT, limit=200,
                      aspect_filter=bf(brand))
        for i in (d or {}).get("itemSummaries", []) or []:
            s = i.get("seller", {})
            u = s.get("username")
            if u:
                sellers[u] += 1
                feedback[u] = (s.get("feedbackScore"),
                               s.get("feedbackPercentage"))

    n = sum(sellers.values())
    print(f"   {len(sellers)} distinct sellers across {n} listings\n")
    for s, c in sellers.most_common(12):
        fb, pctg = feedback.get(s, (None, None))
        print(f"      {c:>4}  {s[:26]:<26} fb={fb}  {pctg}%")

    top10 = sum(c for _, c in sellers.most_common(10))
    print(f"\n   top 10 sellers hold {top10/max(n,1)*100:.1f}% of listings")
    solo = sum(1 for c in sellers.values() if c == 1)
    print(f"   {solo} sellers ({solo/max(len(sellers),1)*100:.0f}%)"
          f" have a single listing")
    print("\n   NOTE: seller usernames are eBay user data. You are not")
    print("   exempt, so anything stored here must be deletable when")
    print("   an account-deletion notice arrives at your Worker.")

    res["sellers"] = {"distinct": len(sellers), "listings": n,
                      "top10_pct": round(top10 / max(n, 1) * 100, 1)}


# ================================================================== main

TESTS = {
    "F1": f1_ceiling, "F2": f2_ratelimit, "F3": f3_partition, "F4": f4_regex,
    "N1": n1_full_sweep, "N2": n2_sort_reach, "N3": n3_stability,
    "N4": n4_currency, "N5": n5_epid, "N6": n6_age, "N7": n7_dimensions,
    "N8": n8_size, "N9": n9_errors, "N10": n10_sellers,
}
ORDER = ["F1", "F2", "F3", "F4", "N1", "N2", "N3", "N4", "N5", "N6",
         "N7", "N8", "N9", "N10"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--marketplace", default="EBAY_GB")
    p.add_argument("--currency", default="GBP")
    p.add_argument("--test", nargs="*", default=ORDER)
    p.add_argument("--light", action="store_true")
    p.add_argument("--sweep-brand", default="TUDOR")
    a = p.parse_args()

    OUT.mkdir(exist_ok=True)
    res = {"run_at": datetime.now(timezone.utc).isoformat(),
           "marketplace": a.marketplace, "currency": a.currency,
           "light": a.light}

    print(f"\n  FINAL DIAGNOSTIC  |  {a.marketplace} / {a.currency}"
          f"{'  [light]' if a.light else ''}")
    token()
    print("  auth ok")
    t0 = time.time()

    for t in [k for k in ORDER if k in a.test]:
        try:
            if t == "N1":
                n1_full_sweep(a.marketplace, a.currency, res, a.light,
                              a.sweep_brand)
            else:
                TESTS[t](a.marketplace, a.currency, res, a.light)
        except Exception as e:
            print(f"\n  {t} crashed: {type(e).__name__}: {e}")

    print(f"\n{'=' * 72}\n  TOTALS\n{'=' * 72}")
    print(f"   calls: {sum(CALLS.values())}   elapsed: {time.time()-t0:.0f}s")
    for k, v in CALLS.most_common():
        print(f"      {v:>5}  {k}")

    res["calls"] = dict(CALLS)
    res["calls_total"] = sum(CALLS.values())
    with open(OUT / "report4.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n  -> {OUT / 'report4.json'}\n")


if __name__ == "__main__":
    main()
import requests
import json
import os
import random
import itertools

USED_TOPICS_FILE = "used_topics.json"

# Tier-1 English-speaking countries with highest YouTube RPM
TIER1_REGIONS = ["us", "us", "us", "gb", "ca", "au"]

# ============================================================
# ROOT KEYWORDS — these are just "entry points"
# The machine recurses into YouTube autocomplete to generate
# HUNDREDS of unique finance/business/motivation queries.
# No finite pool. No rotation. Fresh every run.
# ============================================================
ROOT_KEYWORDS = [
    "how to make money",
    "how to save money",
    "how to invest",
    "how to build wealth",
    "how to start a business",
    "how to grow a business",
    "how to be rich",
    "how to be successful",
    "how to be disciplined",
    "how to think like a rich person",
    "why rich people",
    "why poor people",
    "money mindset",
    "financial freedom",
    "passive income",
    "side hustle",
    "how to retire early",
    "how to pay off debt",
    "how to budget",
    "how to negotiate",
    "how to earn more",
    "how to save your first",
    "how millionaires",
    "how billionaires",
    "business ideas",
    "small business tips",
    "entrepreneur mindset",
    "success habits",
    "discipline motivation",
    "self improvement money",
    "how to change your life",
    "how to stop being poor",
    "how to escape the rat race",
    "how to become financially free",
    "how money works",
    "how banks work",
    "how the economy works",
    "how inflation works",
    "how to protect your wealth",
    "how to build multiple income streams",
]

# Question starters to expand depth
QUESTION_PREFIXES = [
    "how to", "why do", "what is", "what if", "when should",
    "where to", "which is better", "who is", "can you", "should i",
]


# ============================================================
# MEMORY (prevents topic repeats across ALL runs, forever)
# ============================================================

def load_used_topics():
    if os.path.exists(USED_TOPICS_FILE):
        try:
            with open(USED_TOPICS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


def save_used_topics(used):
    # Keep ALL used topics (not just last 200) — we want permanent memory
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, indent=2)


# ============================================================
# AUTOCOMPLETE FETCHER
# ============================================================

def yt_suggest(query, region="us"):
    """Fetch live YouTube autocomplete suggestions for a query/country."""
    try:
        url = (
            f"http://suggestqueries.google.com/complete/search"
            f"?client=firefox&ds=yt&hl=en&gl={region}"
            f"&q={requests.utils.quote(query)}"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data[1] if len(data) > 1 else []
        return []
    except Exception as e:
        print(f"⚠️ Suggest failed for '{query}' [{region}]: {e}")
        return []


# ============================================================
# RECURSIVE MINING — pulls hundreds of unique queries per run
# ============================================================

def mine_topics(used_set, target_count=50):
    """
    Recursively expand root keywords through YouTube autocomplete.
    Returns up to `target_count` unique, unused finance queries.
    """
    random.shuffle(ROOT_KEYWORDS)
    found = []
    seen = set()

    # Level 1: query each root, collect suggestions
    level1_queries = []
    for root in ROOT_KEYWORDS[:15]:  # take 15 roots per run
        region = random.choice(TIER1_REGIONS)
        suggestions = yt_suggest(root, region=region)
        random.shuffle(suggestions)
        for s in suggestions:
            s_clean = s.strip().lower()
            if not s_clean or s_clean in seen:
                continue
            seen.add(s_clean)
            level1_queries.append((s_clean, region))

        if len(level1_queries) >= target_count * 2:
            break

    # Level 2: expand the level-1 queries further (long-tail goldmine)
    random.shuffle(level1_queries)
    level2_queries = []
    for query, _ in level1_queries[:25]:
        region = random.choice(TIER1_REGIONS)
        suggestions = yt_suggest(query, region=region)
        random.shuffle(suggestions)
        for s in suggestions:
            s_clean = s.strip().lower()
            if not s_clean or s_clean in seen:
                continue
            seen.add(s_clean)
            level2_queries.append((s_clean, region))

        if len(level1_queries) + len(level2_queries) >= target_count * 3:
            break

    # Combine all candidates
    all_candidates = level1_queries + level2_queries
    random.shuffle(all_candidates)

    # Filter: keep only finance/money/business/motivation related + not used
    FINANCE_MARKERS = [
        "money", "rich", "wealth", "invest", "finance", "financ", "business",
        "income", "salary", "job", "career", "budget", "save", "saving",
        "debt", "loan", "credit", "bank", "stock", "invest", "trade", "trading",
        "millionaire", "billionaire", "success", "successful", "discipline",
        "motivat", "hustle", "entrepreneur", "profit", "revenue", "tax",
        "retire", "retirement", "pension", "401k", "ira", "fund", "asset",
        "dollar", "dollars", "dollar", "euro", "pound", "cash", "coin",
        "passive", "side hustle", "gig", "freelance", "ecommerce", "dropship",
        "real estate", "rental", "landlord", "mortgage", "property",
        "compound", "interest", "dividend", "yield", "return", "portfolio",
        "hedge", "crypto", "bitcoin", "forex", "gold", "silver",
        "boss", "employee", "employer", "startup", "founder", "ceo",
        "frugal", "thrifty", "spend", "spending", "shopping",
        "raise", "promotion", "interview", "resume",
    ]

    def is_finance_related(t):
        return any(marker in t for marker in FINANCE_MARKERS)

    for candidate, region in all_candidates:
        if len(found) >= target_count:
            break
        if not is_finance_related(candidate):
            continue
        if candidate in used_set:
            continue
        # Avoid near-duplicates of already used topics
        if any(candidate in u or u in candidate for u in used_set if len(u) > 20):
            continue
        found.append(candidate)

    print(f"💎 Mined {len(found)} fresh finance topics from {len(all_candidates)} candidates")
    return found


# ============================================================
# MAIN
# ============================================================

def research_topics():
    print("🔍 Mining tier-1 YouTube trends (US/UK/CA/AU) — finance/business/motivation only...")
    used = load_used_topics()
    print(f"📚 Previously used: {len(used)} topics (never repeats)")

    candidates = mine_topics(set(used), target_count=30)

    if len(candidates) < 5:
        print("⚠️ Not enough fresh candidates — falling back to broader mining")
        # Broaden by dropping finance filter as a last resort
        extra = mine_topics(set(used), target_count=20)
        candidates.extend([c for c in extra if c not in candidates])

    random.shuffle(candidates)
    selected = candidates[:5]

    # Safety fallback if still too few (should never happen)
    while len(selected) < 5:
        selected.append(f"how to make money online part {len(selected)+1}")

    topics = {
        "long_finance": selected[0],
        "long_general": selected[1],
        "short_finance": selected[2],
        "short_general": selected[3],
        "short_curious": selected[4],
    }

    # Save all newly used
    used.extend([t.lower() for t in selected])
    save_used_topics(used)
    print(f"📚 Now tracking {len(used)} used topics (memory grows forever)")

    return topics


if __name__ == "__main__":
    result = research_topics()
    print("\n📌 Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")

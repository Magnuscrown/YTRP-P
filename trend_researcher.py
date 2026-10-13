import requests
import json
import os
import random

USED_TOPICS_FILE = "used_topics.json"

# Tier-1 English-speaking countries (highest YouTube RPM)
TIER1_REGIONS = ["us", "us", "us", "gb", "ca", "au"]

# ============================================================
# POOL 1: FINANCE (money, business, wealth, motivation)
# ============================================================
FINANCE_ROOTS = [
    "how to make money", "how to save money", "how to invest",
    "how to build wealth", "how to start a business",
    "how to grow a business", "how to be rich",
    "money mindset", "financial freedom", "passive income",
    "side hustle", "how to retire early", "how to pay off debt",
    "how to budget", "how to negotiate salary",
    "how millionaires", "how billionaires",
    "business ideas", "small business tips", "entrepreneur mindset",
    "how to think like a rich person", "why rich people",
    "how to escape the rat race", "how money works",
    "how banks work", "how to build multiple income streams",
    "success habits", "discipline motivation",
    "how to earn more", "how to change your life",
]

FINANCE_MARKERS = [
    "money", "rich", "wealth", "invest", "finance", "financ",
    "business", "income", "salary", "budget", "save", "saving",
    "debt", "loan", "credit", "bank", "stock", "trade", "trading",
    "millionaire", "billionaire", "success", "successful",
    "discipline", "motivat", "hustle", "entrepreneur", "profit",
    "revenue", "tax", "retire", "pension", "401k", "ira", "fund",
    "asset", "cash", "passive", "side hustle", "freelance",
    "ecommerce", "dropship", "real estate", "rental", "landlord",
    "mortgage", "property", "compound", "interest", "dividend",
    "yield", "portfolio", "crypto", "bitcoin", "forex", "gold",
    "boss", "employee", "employer", "startup", "founder", "ceo",
    "frugal", "thrifty", "spend", "spending", "raise",
    "promotion", "interview", "resume", "earn", "money mindset",
]

# ============================================================
# POOL 2: GENERAL (curious facts, psychology, science, history)
# ============================================================
GENERAL_ROOTS = [
    "why do people", "how does", "why is", "what is",
    "psychology facts", "habits of successful people",
    "science explained", "history facts", "space facts",
    "ocean facts", "human body facts", "animal facts",
    "why do we dream", "how the brain works",
    "how things are made", "amazing inventions",
    "things you didn't know", "most searched questions",
    "life hacks everyone should know", "how the internet works",
    "how ai works", "future technology",
    "ancient civilizations", "world records",
    "hidden rules of society", "everyday objects explained",
    "why does the body", "how to improve your memory",
    "habits that change your life", "psychology of attraction",
]

# ============================================================
# POOL 3: CURIOUS (what if scenarios)
# ============================================================
CURIOUS_ROOTS = [
    "what if you woke up in",
    "what if money didn't exist",
    "what if the internet disappeared",
    "what if humans could fly",
    "what if the sun disappeared",
    "what if you could time travel",
    "what if gravity stopped",
    "what if you never slept",
    "what if the oceans dried up",
    "what if ai took over",
    "what if you were the last person on earth",
    "what if the moon crashed",
    "what if electricity stopped",
    "what if you could read minds",
    "what if you lived forever",
    "what if you could teleport",
    "what if ants were as big as humans",
    "what if you could freeze time",
    "what if the earth stopped spinning",
    "what if you never felt pain",
    "what if everyone was rich",
    "what if you could see in the dark",
    "what if animals could talk",
    "what if we lived on mars",
    "what if you could live underwater",
]


# ============================================================
# MEMORY (permanent, prevents repeats forever)
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
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, indent=2)


# ============================================================
# AUTOCOMPLETE FETCHER
# ============================================================

def yt_suggest(query, region="us"):
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
        print(f"⚠️ Suggest failed '{query}' [{region}]: {e}")
        return []


# ============================================================
# RECURSIVE MINER (generic — used by all 3 pools)
# ============================================================

def mine_from_roots(roots, used_set, filter_fn, target=30, label="POOL"):
    """Recursively expand roots through YouTube autocomplete."""
    random.shuffle(roots)
    found = []
    seen = set()
    all_candidates = []

    # Level 1: query roots
    for root in roots[:15]:
        region = random.choice(TIER1_REGIONS)
        for s in yt_suggest(root, region=region):
            s_clean = s.strip().lower()
            if s_clean and s_clean not in seen:
                seen.add(s_clean)
                all_candidates.append(s_clean)

    # Level 2: expand a handful of level-1 results (long-tail mining)
    random.shuffle(all_candidates)
    level1_copy = all_candidates[:20]
    for q in level1_copy:
        region = random.choice(TIER1_REGIONS)
        for s in yt_suggest(q, region=region):
            s_clean = s.strip().lower()
            if s_clean and s_clean not in seen:
                seen.add(s_clean)
                all_candidates.append(s_clean)

    random.shuffle(all_candidates)

    for c in all_candidates:
        if len(found) >= target:
            break
        if not filter_fn(c):
            continue
        if c in used_set:
            continue
        if any(c in u or u in c for u in used_set if len(u) > 20):
            continue
        found.append(c)

    print(f"💎 [{label}] Mined {len(found)} fresh topics from {len(all_candidates)} candidates")
    return found


def finance_filter(t):
    return any(m in t for m in FINANCE_MARKERS)


def general_filter(t):
    # Skip anything finance-flavored so the two channels stay distinct
    if finance_filter(t):
        return False
    # Skip empty/short
    if len(t) < 12:
        return False
    return True


def curious_filter(t):
    return t.startswith("what if") or t.startswith("what would happen")


# ============================================================
# MAIN
# ============================================================

def research_topics():
    print("🔍 Mining tier-1 YouTube trends (US/UK/CA/AU) — 3 pools: finance | general | curious...")
    used = load_used_topics()
    print(f"📚 Previously used: {len(used)} topics")

    used_set = set(used)

    # --- Pool 1: Finance ---
    finance_candidates = mine_from_roots(
        FINANCE_ROOTS, used_set, finance_filter, target=20, label="FINANCE"
    )

    # --- Pool 2: General ---
    general_candidates = mine_from_roots(
        GENERAL_ROOTS, used_set | set(finance_candidates),
        general_filter, target=20, label="GENERAL"
    )

    # --- Pool 3: Curious ---
    curious_candidates = mine_from_roots(
        CURIOUS_ROOTS, used_set | set(finance_candidates) | set(general_candidates),
        curious_filter, target=15, label="CURIOUS"
    )

    # Fallbacks if any pool came up short
    if len(finance_candidates) < 2:
        finance_candidates += ["how to make money online", "how to save money fast"]
    if len(general_candidates) < 2:
        general_candidates += ["psychology facts", "why do we dream"]
    if len(curious_candidates) < 1:
        curious_candidates += ["what if the internet disappeared"]

    random.shuffle(finance_candidates)
    random.shuffle(general_candidates)
    random.shuffle(curious_candidates)

    topics = {
        "long_finance":  finance_candidates[0],
        "short_finance": finance_candidates[1],
        "long_general":  general_candidates[0],
        "short_general": general_candidates[1],
        "short_curious": curious_candidates[0],
    }

    used.extend([t.lower() for t in topics.values()])
    save_used_topics(used)
    print(f"📚 Now tracking {len(used)} used topics (grows forever)")

    return topics


if __name__ == "__main__":
    result = research_topics()
    print("\n📌 Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")

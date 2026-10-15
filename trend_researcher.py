"""Mines live YouTube autocomplete (finance only) and remembers used topics forever."""
import json
import random
import re
import time

import requests

from config import USED_TOPICS_FILE

ROOTS = [
    "how to make money", "how to invest", "how to start a business", "how to get rich",
    "how to save money", "how to build wealth", "how to become a millionaire",
    "how to make passive income", "how to start investing", "how to pay off debt",
    "how to budget", "how to retire early", "how to build credit", "side hustle",
    "passive income ideas", "money habits", "rich vs poor", "why people stay poor",
    "investing for beginners", "stock market for beginners", "how to grow money",
    "how to get out of debt", "how to start a side hustle", "millionaire mindset",
    "wealth mindset", "financial freedom", "how to manage money", "money mistakes",
    "how the rich think", "how billionaires invest", "how to make money online",
    "how to own a company", "how to start an llc", "real estate investing",
    "index funds", "compound interest", "how to save 10000", "how to stop being broke",
    "how to build an emergency fund", "business ideas", "how to become wealthy",
    "money lessons", "financial habits", "how to earn more money",
]
MARKERS = [
    "money", "rich", "invest", "wealth", "business", "income", "stock", "passive", "saving",
    "savings", "budget", "millionaire", "billionaire", "financial", "finance", "debt", "credit",
    "hustle", "retire", "tax", "profit", "entrepreneur", "broke", "poor", "salary", "earn",
    "fund", "company", "llc", "real estate", "compound", "freedom",
]
JUNK = ["movie", "song", "lyrics", "game", "reaction", "full episode", "meme", "tiktok",
        "login", "app download", "hindi", "urdu", "tamil", "telugu", "in nigeria", "in india",
        "in pakistan", "in kenya", "in ghana"]
COUNTRIES = ["us", "us", "us", "gb", "ca", "au"]   # US gets 3x weight
URL = "https://suggestqueries.google.com/complete/search"


def _suggest(q, gl):
    try:
        r = requests.get(
            URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"},
            params={"client": "firefox", "ds": "yt", "q": q, "gl": gl, "hl": "en"},
        )
        r.raise_for_status()
        return [s.strip().lower() for s in r.json()[1] if isinstance(s, str)]
    except Exception:
        return []


def _norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def _words(t):
    return set(_norm(t).split())


def _similar(a, b):
    wa, wb = _words(a), _words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.7


def load_used():
    try:
        return json.loads(USED_TOPICS_FILE.read_text())
    except Exception:
        return []


def mark_used(topic):
    used = load_used()
    used.append(topic)
    USED_TOPICS_FILE.write_text(json.dumps(used, indent=1))


def _is_finance(s):
    return any(m in s for m in MARKERS)


def _clean_ok(s):
    n = len(s.split())
    return 3 <= n <= 12 and s.isascii() and not any(j in s for j in JUNK)


def mine():
    level1 = []
    for root in ROOTS:
        level1 += _suggest(root, random.choice(COUNTRIES))
        time.sleep(0.1)
    level1 = list(dict.fromkeys(level1))
    level2 = []
    for s in random.sample(level1, min(20, len(level1))):
        level2 += _suggest(s, random.choice(COUNTRIES))
        time.sleep(0.1)
    pool = list(dict.fromkeys(level1 + level2))
    return [s for s in pool if _is_finance(s) and _clean_ok(s)]


def pick_topics(n_long=1, n_short=3, n_spare=6):
    used = [_norm(u) for u in load_used()]
    used_set = set(used)
    cands = [c for c in mine() if _norm(c) not in used_set and not any(_similar(c, u) for u in used[-300:])]
    random.shuffle(cands)
    chosen = []
    for c in cands:
        if not any(_similar(c, x) for x in chosen):
            chosen.append(c)
        if len(chosen) == n_long + n_short + n_spare:
            break
    print(f"[trends] {len(cands)} fresh finance candidates")
    if len(chosen) < n_long + n_short:
        raise RuntimeError("Not enough fresh finance topics found")
    return chosen[:n_long], chosen[n_long:n_long + n_short], chosen[n_long + n_short:]

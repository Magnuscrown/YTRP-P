"""Finds what people in the USA, UK, Canada and Australia really search on YouTube about money/rich/poor,
then turns each idea into a Rich vs Poor Psychology title. Numbers are NEVER forced.
Every video in a run gets a different angle, hook style and ending style (see formats.py)."""
import json, random, re, time
import requests
from config import USED_TOPICS_FILE, SPECS, YOUTUBE_API_KEY, CHANNEL_FOCUS
from llm import ask
from formats import FORMATS, HOOK_STYLES, ENDINGS

COUNTRIES = [
    {"geo": "US", "name": "USA"},
    {"geo": "GB", "name": "UK"},
    {"geo": "CA", "name": "Canada"},
    {"geo": "AU", "name": "Australia"},
]

SEEDS = [
    "why poor people stay poor", "why rich people", "how rich people think", "poor mindset", "rich mindset",
    "money psychology", "why am i always broke", "habits of rich people", "how to stop being poor",
    "poor vs rich", "wealthy mindset", "why do i spend money", "scarcity mindset", "why rich people get richer",
    "money habits", "paycheck to paycheck", "how to think like a millionaire",
]

_yt_cache = {"videos": [], "ts": 0}

# ------------------------------------------------------------------ what people really search
def _autocomplete(q, geo):
    """YouTube search suggestions = what real people in that country type into the search box."""
    try:
        r = requests.get("https://suggestqueries.clients.google.com/complete/search",
                         params={"client": "firefox", "ds": "yt", "q": q, "hl": "en", "gl": geo}, timeout=12)
        if r.status_code != 200: return []
        data = r.json()
        return [s for s in data[1] if isinstance(s, str) and 3 <= len(s.split()) <= 10]
    except Exception:
        return []

def _yt_most_popular(region):
    if not YOUTUBE_API_KEY: return []
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "snippet", "chart": "mostPopular", "regionCode": region, "maxResults": 25, "key": YOUTUBE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200: return []
        return [it["snippet"]["title"] for it in r.json().get("items", []) if 2 <= len(it["snippet"]["title"].split()) <= 12]
    except Exception: return []

def _yt_search_finance(region):
    """Most-viewed videos from the LAST 14 DAYS about rich/poor/money psychology in this country."""
    if not YOUTUBE_API_KEY: return []
    url = "https://www.googleapis.com/youtube/v3/search"
    after = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 14 * 86400))
    out = []
    for q in ["rich vs poor", "money mindset", "why poor people stay poor", "how rich people think"]:
        params = {"part": "snippet", "q": q, "type": "video", "order": "viewCount", "regionCode": region,
                  "publishedAfter": after, "maxResults": 10, "key": YOUTUBE_API_KEY}
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                for it in r.json().get("items", []):
                    ti = it["snippet"]["title"]
                    if 2 <= len(ti.split()) <= 12: out.append(ti)
        except Exception: pass
    return out

def _dedupe(ideas):
    seen, uniq = set(), []
    for x in ideas:
        k = x.lower().strip()
        if k not in seen and _is_target_country(x):
            seen.add(k); uniq.append(x)
    return uniq

def fetch_trends(force=False):
    """1) What is trending on YouTube right now in US/GB/CA/AU. 2) If that gives too little, real search suggestions."""
    now = time.time()
    if not force and _yt_cache["videos"] and now - _yt_cache["ts"] < 6 * 3600:
        return _yt_cache["videos"]
    ideas = []
    for c in COUNTRIES:
        ideas += _yt_search_finance(c["geo"]) + _yt_most_popular(c["geo"])
    ideas = _dedupe(ideas)
    source = "YouTube trending"
    if len(ideas) < 5:
        for c in COUNTRIES:
            for seed in random.sample(SEEDS, 4):
                ideas += _autocomplete(seed, c["geo"])
        ideas = _dedupe(ideas)
        source = "search suggestions (fallback)"
    _yt_cache["videos"] = ideas
    _yt_cache["ts"] = now
    print(f"[trends] {len(ideas)} ideas from {source} in US/GB/CA/AU")
    return ideas

def _is_target_country(title: str) -> bool:
    t = " " + title.lower() + " "
    bad = ["india", "pakistan", "nigeria", "china", "japan", "korea", "brazil", "mexico", "russia", "germany", "france", "cricket", "bollywood", "hindi", "urdu", "tamil"]
    return not any(o in t for o in bad)

def _trend_to_title(trend: str, F: dict):
    prompt = (f"People in the USA, UK, Canada and Australia really search this on YouTube: \"{trend}\"\n"
              f"Turn that idea into a YouTube video title for a channel about the Psychology of Rich vs Poor. "
              f"Angle: {F['title_style']}. "
              "Do not copy any original title, create a fresh angle. The title must make a stranger curious and must be about money psychology (poor mindset vs rich mindset). "
              "Use a number ONLY if the idea naturally has one. Otherwise use NO digits at all. "
              "If the idea has nothing to do with money, wealth, or rich vs poor thinking, answer exactly: SKIP. "
              "Max 14 words. No quotes. Output ONLY the title.")
    def ok(t):
        line = t.strip().splitlines()[0]
        if line.strip().upper().startswith("SKIP"): return True
        return 3 <= len(line.split()) <= 16
    try:
        out = ask(prompt, max_tokens=60, validate=ok, temperature=0.9).strip().splitlines()[0].strip('"* ')
        if out.strip().upper().startswith("SKIP"): return None
        return out
    except Exception:
        return None

# ------------------------------------------------------------------ memory of what was used
def _norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()
def _sim(a, b):
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.7

def load_used():
    try: return json.loads(USED_TOPICS_FILE.read_text())
    except Exception: return []

def mark_used(title, fmt=None, hook=None, ending=None, trend=None):
    """Remembers the title, and the angle (stored as 'fmt:name') so the next run avoids repeating it."""
    used = load_used(); used.append(title)
    if fmt: used.append(f"fmt:{fmt}")
    if hook: used.append(f"hook:{hook}")
    if ending: used.append(f"end:{ending}")
    if trend: used.append(f"trend:{trend}")
    USED_TOPICS_FILE.write_text(json.dumps(used, indent=1))

def choose_formats(kinds):
    """One DIFFERENT angle per video; angles used in recent runs are avoided."""
    recent = [u[4:] for u in load_used()[-80:] if isinstance(u, str) and u.startswith("fmt:")][-8:]
    chosen = []
    for kind in kinds:
        pool = [k for k, f in FORMATS.items() if kind in f["kinds"] and k not in chosen] or [k for k, f in FORMATS.items() if kind in f["kinds"]]
        fresh = [k for k in pool if k not in recent] or pool
        chosen.append(random.choice(fresh))
    return chosen

def _recent_tag(prefix, k):
    return [u[len(prefix):] for u in load_used()[-300:] if isinstance(u, str) and u.startswith(prefix)][-k:]

def choose_styles(n):
    """n DIFFERENT hook techniques and n DIFFERENT ending techniques (of 30 each), avoiding recently used ones."""
    rh, re_ = _recent_tag("hook:", 40), _recent_tag("end:", 40)
    hp = [k for k in HOOK_STYLES if k not in rh] or list(HOOK_STYLES)
    ep = [k for k in ENDINGS if k not in re_] or list(ENDINGS)
    hooks = random.sample(hp, min(n, len(hp)))
    ends = random.sample(ep, min(n, len(ep)))
    while len(hooks) < n: hooks.append(random.choice(list(HOOK_STYLES)))
    while len(ends) < n: ends.append(random.choice(list(ENDINGS)))
    return hooks, ends

def _refine(title0, recent):
    prompt = (f"Rewrite this title to be fresh and curiosity-driven. Do not add numbers. "
              f"Max 14 words. No quotes.\nOriginal: {title0}\nAvoid these: {recent[-8:]}\nOutput ONLY the title.")
    def ok(t):
        return 3 <= len(t.strip().splitlines()[0].split()) <= 16
    try: return ask(prompt, max_tokens=60, validate=ok, temperature=0.9).strip().splitlines()[0].strip('"* ')
    except Exception: return title0[0].upper() + title0[1:]

# ------------------------------------------------------------------ jobs
def new_job(kind, avoid=(), fmt=None, hook_style=None, ending=None, taken=()):
    if fmt not in FORMATS or kind not in FORMATS[fmt]["kinds"]:
        fmt = choose_formats([kind])[0]
    F = FORMATS[fmt]
    hook_style = hook_style if hook_style in HOOK_STYLES else random.choice(list(HOOK_STYLES))
    ending = ending if ending in ENDINGS else random.choice(list(ENDINGS))
    lo, hi = F["beats_long"] if kind == "long" else F["beats_short"]
    beats = random.randint(lo, hi)
    used = load_used() + list(taken)
    base = dict(kind=kind, fmt=fmt, beats=beats, hook_style=hook_style, ending=ending)
    ideas = fetch_trends()
    if ideas:
        pool = ideas[:]
        random.shuffle(pool)
        for trend in pool[:25]:
            if "search:" + trend in avoid or any(u == "trend:" + trend for u in used): continue
            title = _trend_to_title(trend, F)
            if not title or any(_sim(title, u) for u in used[-400:] if not re.match(r"^(fmt|hook|end|trend):", u)): continue
            return dict(base, title=title, tpl="search:" + trend)
    tpls = F["templates"][:]
    random.shuffle(tpls)
    for tpl in tpls * 3:
        if tpl in avoid: continue
        for cand in (_refine(tpl, used), tpl):
            if not any(_sim(cand, u) for u in used[-400:] if not re.match(r"^(fmt|hook|end|trend):", u)):
                return dict(base, title=cand, tpl=tpl)
    raise RuntimeError("Could not create a fresh title")

def pick_jobs():
    kinds = ["long", "short", "short", "short"]
    fmts = choose_formats(kinds)
    hooks, ends = choose_styles(4)
    jobs, avoid, titles = [], set(), []
    for kind, fmt, hs, en in zip(kinds, fmts, hooks, ends):
        j = new_job(kind, avoid, fmt, hs, en, taken=titles)
        avoid.add(j["tpl"]); titles.append(j["title"]); jobs.append(j)
        print(f"[topics] {kind} ({j['fmt']}, hook={j['hook_style']}, end={j['ending']}): {j['title']}")
    return jobs

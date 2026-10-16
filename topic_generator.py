"""Creates titles from YouTube trends (US/GB/CA/AU) for the Rich vs Poor Psychology channel."""
import json, random, re, time
import requests
from config import USED_TOPICS_FILE, SPECS, YOUTUBE_API_KEY, CHANNEL_FOCUS
from llm import ask

D, A = "desc", "asc"

COUNTRIES = [
    {"geo": "US", "name": "USA"},
    {"geo": "GB", "name": "UK"},
    {"geo": "CA", "name": "Canada"},
    {"geo": "AU", "name": "Australia"},
]

PSYCHOLOGY_TEMPLATES = [
    ("The psychology of why {n} people stay poor and how the rich avoid it", "Number", D),
    ("{n} subtle habits of the rich that the poor never notice", "Number", D),
    ("How the rich use {n} simple psychological tricks to build wealth", "Number", D),
    ("{n} mindset differences between the rich and the poor", "Number", D),
    ("{n} things poor people do that rich people never do", "Number", D),
    ("The psychology behind {n} money mistakes poor people make", "Number", D),
    ("{n} ways the rich think differently about money than the poor", "Number", D),
    ("{n} signs you have a poor mindset (and how to fix it)", "Number", D),
    ("The rich vs poor guide to {n} everyday money decisions", "Number", D),
    ("{n} habits the poor call normal that the rich call dangerous", "Number", D),
]

NUMW = ["zero","one","two","three","four","five","six","seven","eight","nine","ten"]
_yt_cache = {"videos": [], "ts": 0}

def _yt_most_popular(region):
    if not YOUTUBE_API_KEY: return []
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "snippet", "chart": "mostPopular", "regionCode": region, "maxResults": 25, "key": YOUTUBE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200: return []
        return [{"title": it["snippet"]["title"], "region": region} for it in r.json().get("items", [])
                if 2 <= len(it["snippet"]["title"].split()) <= 12]
    except Exception: return []

def _yt_search_finance(region):
    if not YOUTUBE_API_KEY: return []
    url = "https://www.googleapis.com/youtube/v3/search"
    out = []
    for q in ["how to make money", "personal finance", "rich vs poor", "money mindset", "investing for beginners"]:
        params = {"part": "snippet", "q": q, "type": "video", "order": "viewCount", "regionCode": region, "maxResults": 10, "key": YOUTUBE_API_KEY}
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                for it in r.json().get("items", []):
                    t = it["snippet"]["title"]
                    if 2 <= len(t.split()) <= 12: out.append({"title": t, "region": region})
        except Exception: pass
    return out

def fetch_youtube_trends(force=False):
    now = time.time()
    if not force and _yt_cache["videos"] and now - _yt_cache["ts"] < 6 * 3600:
        return _yt_cache["videos"]
    out = []
    for c in COUNTRIES:
        vids = _yt_most_popular(c["geo"])
        if not vids: vids = _yt_search_finance(c["geo"])
        out.extend(vids)
        if len(out) >= 60: break
    seen, uniq = set(), []
    for v in out:
        k = v["title"].lower()
        if k not in seen:
            seen.add(k); uniq.append(v)
    _yt_cache["videos"] = uniq
    _yt_cache["ts"] = now
    print(f"[yt] {len(uniq)} trending titles from US/GB/CA/AU")
    return uniq

def _is_target_country(title: str) -> bool:
    t = " " + title.lower() + " "
    bad = ["india", "pakistan", "nigeria", "china", "japan", "korea", "brazil", "mexico", "russia", "germany", "france", "cricket", "bollywood"]
    if any(o in t for o in bad): return False
    return True

def _trend_to_title(trend: str, n: int):
    if CHANNEL_FOCUS != "psychology":
        prompt = f"Turn '{trend}' into a finance YouTube title with the number {n}."
    else:
        prompt = (f"A trending YouTube search is: \"{trend}\"\n"
                  f"Turn that into a 'Rich vs Poor Psychology' YouTube video title with exactly the number {n} in it. "
                  f"Style: '{n} [habits/mindset things] the poor do that the rich avoid' or similar. "
                  f"Must contrast the rich and the poor. Must be about money psychology. If the trend has nothing to do with money or rich vs poor, answer exactly: SKIP. "
                  f"Max 14 words. No quotes. Output ONLY the title.")
    def ok(t):
        line = t.strip().splitlines()[0]
        if line.strip().upper().startswith("SKIP"): return True
        return (str(n) in line or NUMW[n] in line.lower()) and 3 <= len(line.split()) <= 16
    try:
        out = ask(prompt, max_tokens=60, validate=ok, temperature=0.9).strip().splitlines()[0].strip('"* ')
        if out.strip().upper().startswith("SKIP"): return None
        return out
    except Exception: return None

def _norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()
def _sim(a, b):
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.7

def load_used():
    try: return json.loads(USED_TOPICS_FILE.read_text())
    except Exception: return []

def mark_used(title):
    used = load_used(); used.append(title)
    USED_TOPICS_FILE.write_text(json.dumps(used, indent=1))

def _refine(title0, n, recent):
    prompt = (f"Rewrite this title to be fresh and curiosity-driven. Keep the number {n}. "
              f"Max 14 words. No quotes.\nOriginal: {title0}\nAvoid these: {recent[-8:]}\nOutput ONLY the title.")
    def ok(t):
        line = t.strip().splitlines()[0]
        return (str(n) in line or NUMW[n] in line.lower()) and 3 <= len(line.split()) <= 16
    try: return ask(prompt, max_tokens=60, validate=ok, temperature=0.9).strip().splitlines()[0].strip('"* ')
    except Exception: return title0[0].upper() + title0[1:]

def new_job(kind, avoid=()):
    lo, hi = SPECS[kind]["n_range"]
    used = load_used()
    yt = fetch_youtube_trends()
    if yt:
        random.shuffle(yt)
        for item in yt[:25]:
            trend = item["title"]
            if not _is_target_country(trend): continue
            n = random.randint(lo, hi)
            title = _trend_to_title(trend, n)
            if not title or any(_sim(title, u) for u in used[-400:]): continue
            return dict(kind=kind, title=title, n=n, label="Number", order=D, tpl="yt:" + trend)
    for _ in range(40):
        tpl, label, order = random.choice(PSYCHOLOGY_TEMPLATES)
        if tpl in avoid: continue
        n = random.randint(lo, hi)
        title = _refine(tpl.format(n=n), n, used)
        if any(_sim(title, u) for u in used[-400:]): continue
        return dict(kind=kind, title=title, n=n, label=label, order=order, tpl=tpl)
    raise RuntimeError("Could not create a fresh title")

def pick_jobs():
    jobs, avoid = [], set()
    for kind in ["long", "short", "short", "short"]:
        j = new_job(kind, avoid)
        avoid.add(j["tpl"]); jobs.append(j)
        print(f"[topics] {kind}: {j['title']}")
    return jobs

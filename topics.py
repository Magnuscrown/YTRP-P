"""
TOPIC FINDER: finds what people are searching for RIGHT NOW, from 5 core sources (+ 2 optional extras), then ranks it.

Core sources (free, no key):  1) YouTube search suggestions  2) Google search suggestions  3) Bing search suggestions
                              4) Google Trends (daily trending searches, USA)  5) Gemini with Google Search turned on
Extras (used if they answer):  Reddit top posts of the week, Hacker News stories
Optional: YOUTUBE_API_KEY -> also checks the competition (top results' views and channel sizes)

  python topics.py                 -> prints the ranked topics, saves out/topic_candidates.json, returns the best unused one
Ideas already used are remembered in used_topics.json (the workflow saves that file back to your repo).
Honest limit: free tools show what is popular, not exact search numbers. Demand is a signal, not a promise of views.
"""
import os, re, sys, json, time, xml.etree.ElementTree as ET
import requests
from series_writer import ask_json, parse_json, PROVIDERS, candidates

OUT = "out"
SEEDS = (os.getenv("TOPIC_SEEDS") or "how to start a business with little money|business ideas 2026|how to buy a business|"
         "how to make money online|side hustle ideas|how rich people think about money|how to save money fast|"
         "passive income ideas").split("|")
HEAD = {"User-Agent": "Mozilla/5.0 (compatible; topic-research/1.0)"}
SOURCES = ["youtube", "google", "bing", "trends", "gemini", "reddit", "hackernews"]


def get(url, **kw):
    try:
        r = requests.get(url, headers=HEAD, timeout=25, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"[skip] {url[:60]}...: {str(e)[:80]}")
        return None


# ------------------------------------------------------------------ Gemini + Google Search (also used by explainer.py)
_grounding_dead = False


def grounded(prompt):
    """Gemini + Google Search tool. Often has NO free quota, so one failure switches it off for the whole run."""
    global _grounding_dead
    if _grounding_dead:
        raise RuntimeError("Gemini search tool unavailable (skipped).")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing (needed for the Google-Search tool).")
    name, base, _, override, prefs = PROVIDERS[0]
    last = ""
    for model in candidates(name, base, key, override, prefs):
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          headers={"x-goog-api-key": key},
                          json={"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]},
                          timeout=180)
        if r.status_code == 200:
            cand = r.json()["candidates"][0]
            text = "".join(p.get("text", "") for p in cand["content"]["parts"])
            chunks = cand.get("groundingMetadata", {}).get("groundingChunks", [])
            return text, [c["web"]["uri"] for c in chunks if "web" in c]
        last = f"{model}: {r.status_code} {r.text[:150]}"
        print("[fail]", last)
        if r.status_code == 429:
            break                   # quota: other Gemini models will say the same
    _grounding_dead = True
    raise RuntimeError("Search-grounded call failed -> " + last)


# ------------------------------------------------------------------ the sources
def suggest(url, q):
    r = get(url, params={"q": q} if "bing" not in url else {"query": q})
    try:
        return [s for s in r.json()[1]] if r else []
    except Exception:
        return []


def collect():
    """Returns {phrase: set(sources)}"""
    found = {}

    def add(src, phrase):
        p = re.sub(r"\s+", " ", str(phrase).lower()).strip()
        if 6 <= len(p) <= 120:
            found.setdefault(p, set()).add(src)

    for seed in SEEDS:
        for q in (seed, "how to " + seed if not seed.startswith("how") else seed + " step by step"):
            for s in suggest("https://suggestqueries.google.com/complete/search?client=firefox&ds=yt", q):
                add("youtube", s)
            for s in suggest("https://suggestqueries.google.com/complete/search?client=firefox", q):
                add("google", s)
            for s in suggest("https://api.bing.com/osjson.aspx", q):
                add("bing", s)
        time.sleep(0.3)

    r = get("https://trends.google.com/trending/rss?geo=US")          # daily trending searches
    if r:
        try:
            for item in ET.fromstring(r.content).iter("item"):
                t = item.find("title")
                if t is not None and t.text:
                    add("trends", t.text)
        except Exception as e:
            print("[skip] trends parse:", e)

    try:                                                              # Gemini + Google Search
        text, _ = grounded("Using Google Search, list 15 questions or topics about money, starting or buying a business, "
                           "side hustles or wealth habits that people are searching for or discussing this week. "
                           'Return JSON only: {"topics": ["..."]}')
        for t in parse_json(text)["topics"]:
            add("gemini", t)
    except Exception as e:
        print("[skip] gemini search:", str(e)[:100])

    for sub in ("Entrepreneur", "sidehustle", "smallbusiness"):       # extras (often blocked, that is fine)
        r = get(f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=15")
        if r:
            try:
                for c in r.json()["data"]["children"]:
                    add("reddit", c["data"]["title"])
            except Exception:
                pass
    r = get("https://hn.algolia.com/api/v1/search?query=startup%20business&tags=story&hitsPerPage=15")
    if r:
        try:
            for h in r.json()["hits"]:
                add("hackernews", h.get("title") or "")
        except Exception:
            pass
    counts = {s: sum(1 for v in found.values() if s in v) for s in SOURCES}
    print("[sources] phrases found per source:", counts)
    return found


# ------------------------------------------------------------------ rank
def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in {"how", "to", "a", "the", "of", "in", "and", "with", "for", "what", "is", "i", "do", "it"}}


def evidence(topic_phrase, found):
    """In how many DIFFERENT sources does a similar phrase appear (>= 60% of the words in common)?"""
    tw = words(topic_phrase)
    if not tw:
        return set()
    srcs = set()
    for phrase, ss in found.items():
        pw = words(phrase)
        if pw and len(tw & pw) / min(len(tw), len(pw)) >= 0.6:
            srcs |= ss
    return srcs


def competition(phrase):
    """Optional: top YouTube results for the phrase -> median views and how many big channels."""
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        return None
    try:
        s = requests.get("https://www.googleapis.com/youtube/v3/search", timeout=30,
                         params={"part": "snippet", "q": phrase, "type": "video", "maxResults": 10, "key": key}).json()
        vids = [i["id"]["videoId"] for i in s["items"]]
        chans = list({i["snippet"]["channelId"] for i in s["items"]})
        v = requests.get("https://www.googleapis.com/youtube/v3/videos", timeout=30,
                         params={"part": "statistics", "id": ",".join(vids), "key": key}).json()
        views = sorted(int(i["statistics"].get("viewCount", 0)) for i in v["items"])
        c = requests.get("https://www.googleapis.com/youtube/v3/channels", timeout=30,
                         params={"part": "statistics", "id": ",".join(chans), "key": key}).json()
        big = sum(1 for i in c["items"] if int(i["statistics"].get("subscriberCount", 0)) > 1_000_000)
        return {"median_views": views[len(views) // 2], "big_channels": big, "of": len(chans)}
    except Exception as e:
        print("[skip] competition check:", str(e)[:80])
        return None


def used_topics():
    try:
        return json.load(open("used_topics.json"))
    except Exception:
        return []


def rank(found):
    pool = sorted(found.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:120]
    listing = "\n".join(f"- {p}  [{', '.join(sorted(s))}]" for p, s in pool)
    res = ask_json(f"""These are phrases people are searching for or discussing right now (with the sources that showed them):
{listing}

Pick the 8 best topics for a 10-minute YouTube explainer video that compares two approaches (for example "with little money vs with lots
of money", "employee vs owner", "beginner vs experienced"). The topic must be explainable TRUTHFULLY (no get-rich-quick promises).
Return JSON: {{"topics": [{{"topic": "honest video title idea", "search_phrase": "the exact phrase people type",
"angle": "side A vs side B in one line", "demand": 1-10}}]}}""", "You are a careful YouTube topic researcher. Reply with JSON only.")["topics"]
    avoid = [words(u) for u in used_topics()]
    ranked = []
    for t in res:
        tw = words(t["topic"] + " " + t["search_phrase"])
        if any(a and len(tw & a) / min(len(tw), len(a)) >= 0.7 for a in avoid):
            continue                                                  # already used
        srcs = evidence(t["search_phrase"], found) | evidence(t["topic"], found)
        t["sources"] = sorted(srcs)
        t["score"] = len(srcs) * 2 + float(t.get("demand", 5))
        ranked.append(t)
    ranked.sort(key=lambda t: -t["score"])
    for t in ranked[:3]:                                              # competition check only for the best few
        t["competition"] = competition(t["search_phrase"])
        c = t["competition"]
        if c and c["of"] and c["big_channels"] / c["of"] > 0.6:
            t["score"] -= 3
    ranked.sort(key=lambda t: -t["score"])
    return ranked


def best_topic():
    found = collect()
    if not found:
        raise SystemExit("No search data came back from any source. Check the log for [skip] lines.")
    ranked = rank(found)
    if not ranked:
        raise SystemExit("All good topics were already used. Add new seeds with TOPIC_SEEDS.")
    os.makedirs(OUT, exist_ok=True)
    json.dump(ranked, open(f"{OUT}/topic_candidates.json", "w"), indent=2, ensure_ascii=False)
    for i, t in enumerate(ranked[:5], 1):
        print(f"{i}. {t['topic']}  (score {t['score']:.0f}, seen in: {', '.join(t['sources']) or 'none'})")
    return ranked[0]


def mark_used(topic):
    u = used_topics()
    u.append(topic)
    json.dump(u, open("used_topics.json", "w"), indent=1)


if __name__ == "__main__":
    print(json.dumps(best_topic(), indent=2, ensure_ascii=False))

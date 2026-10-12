"""
WEB SEARCH with several engines at once (so one failing or running out of quota does not stop the pipeline).

  search("query") -> [{"title", "url", "snippet", "engine"}, ...]   merged from every engine that works

Engines (each is used only if available):
  DuckDuckGo  - no key needed (pip install ddgs)             Wikipedia - no key needed
  Tavily      - TAVILY_API_KEY  (free plan at tavily.com, as far as I know about 1,000 searches a month: check their page)
  Brave       - BRAVE_API_KEY   (api.search.brave.com)         Google - GOOGLE_CSE_KEY + GOOGLE_CSE_CX (Programmable Search, about 100 free a day)
Honest limit: we only read the short text snippets the engines return, not whole web pages.
"""
import os, re, time, html, requests

HEAD = {"User-Agent": "recap-pipeline/1.0 (personal project; contact via GitHub)"}
_cache = {}
_dead = set()          # engines that failed hard (bad key, quota): skipped for the rest of the run


def _tavily(q, n):
    r = requests.post("https://api.tavily.com/search", timeout=40,
                      json={"api_key": os.environ["TAVILY_API_KEY"], "query": q, "max_results": n, "search_depth": "basic"})
    r.raise_for_status()
    return [{"title": x["title"], "url": x["url"], "snippet": x.get("content", "")} for x in r.json()["results"]]


def _brave(q, n):
    r = requests.get("https://api.search.brave.com/res/v1/web/search", timeout=40, params={"q": q, "count": n},
                     headers={"X-Subscription-Token": os.environ["BRAVE_API_KEY"], "Accept": "application/json"})
    r.raise_for_status()
    return [{"title": x["title"], "url": x["url"], "snippet": html.unescape(re.sub(r"<[^>]+>", "", x.get("description", "")))}
            for x in r.json().get("web", {}).get("results", [])]


def _google(q, n):
    r = requests.get("https://www.googleapis.com/customsearch/v1", timeout=40,
                     params={"key": os.environ["GOOGLE_CSE_KEY"], "cx": os.environ["GOOGLE_CSE_CX"], "q": q, "num": min(n, 10)})
    r.raise_for_status()
    return [{"title": x["title"], "url": x["link"], "snippet": x.get("snippet", "")} for x in r.json().get("items", [])]


def _ddg(q, n):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    return [{"title": x.get("title", ""), "url": x.get("href", ""), "snippet": x.get("body", "")}
            for x in DDGS().text(q, max_results=n)]


def _wikipedia(q, n):
    r = requests.get("https://en.wikipedia.org/w/api.php", headers=HEAD, timeout=30,
                     params={"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": min(n, 3)})
    r.raise_for_status()
    return [{"title": x["title"], "url": f"https://en.wikipedia.org/?curid={x['pageid']}",
             "snippet": html.unescape(re.sub(r"<[^>]+>", "", x["snippet"]))} for x in r.json()["query"]["search"]]


ENGINES = [("tavily", "TAVILY_API_KEY", _tavily), ("brave", "BRAVE_API_KEY", _brave),
           ("google", "GOOGLE_CSE_KEY", _google), ("duckduckgo", None, _ddg), ("wikipedia", None, _wikipedia)]


def search(query, n=6):
    key = (query, n)
    if key in _cache:
        return _cache[key]
    out, seen = [], set()
    for name, env, fn in ENGINES:
        if name in _dead or (env and not os.getenv(env)):
            continue
        try:
            for x in fn(query, n):
                if x["url"] and x["url"] not in seen:
                    seen.add(x["url"])
                    out.append({**x, "snippet": x["snippet"][:500], "engine": name})
        except Exception as e:
            msg = str(e)[:100]
            print(f"[search:{name}] {msg}")
            if any(c in msg for c in ("401", "403", "429", "402")):
                _dead.add(name)             # key/quota problem: do not keep hammering it
    time.sleep(0.5)
    _cache[key] = out
    return out


def snippets_text(results, limit=8):
    return "\n".join(f"[{i + 1}] {r['title']} ({r['url']}): {r['snippet']}" for i, r in enumerate(results[:limit]))

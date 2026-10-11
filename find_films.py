"""
FILM FINDER: lists the MOST-DOWNLOADED films on the Internet Archive that carry a reusable licence.

  python find_films.py                       -> popular films with CC0 / Public Domain Mark / CC BY licence written on the page
  python find_films.py --short               -> only short films (under 40 minutes)
  python find_films.py --long                -> only feature-length (over 60 minutes)
  python find_films.py --candidates          -> popular old films with NO licence written on the page.
                                                 These are UNVERIFIED: you must check their copyright status yourself.
Needs: pip install requests        (run on your laptop; the result gives you the ID for recap.py / the Movie recap workflow)
"""
import re, sys, requests

OK_LICENSE = ("creativecommons.org/publicdomain/zero", "creativecommons.org/publicdomain/mark",
              "creativecommons.org/licenses/by/")


def minutes(runtime):
    """Archive 'runtime' comes in many formats: '01:23:45', '83:10', '90 min', '5400'."""
    if not runtime:
        return None
    r = str(runtime).strip().lower()
    m = re.match(r"^(\d+):(\d+):(\d+)", r)
    if m:
        return int(m[1]) * 60 + int(m[2]) + int(m[3]) / 60
    m = re.match(r"^(\d+):(\d+)$", r)
    if m:
        return int(m[1]) + int(m[2]) / 60
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(min|minutes|m)\b", r)
    if m:
        return float(m[1])
    m = re.match(r"^(\d+(?:\.\d+)?)$", r)
    if m:
        v = float(m[1])
        return v / 60 if v > 300 else v      # big numbers are seconds
    return None


HEADERS = {"User-Agent": "recap-pipeline/1.0 (personal project)"}
FIELDS = ["identifier", "title", "downloads", "licenseurl", "runtime", "creator"]

# The exact licence URLs we accept. We search for each one by its exact text (more reliable than wildcards).
LICENSE_URLS = []
for scheme in ("http", "https"):
    for v in ("2.0", "2.5", "3.0", "4.0"):
        LICENSE_URLS.append(f"{scheme}://creativecommons.org/licenses/by/{v}/")
    LICENSE_URLS.append(f"{scheme}://creativecommons.org/publicdomain/zero/1.0/")
    LICENSE_URLS.append(f"{scheme}://creativecommons.org/publicdomain/mark/1.0/")


def search(query, rows=200):
    """One Internet Archive search, most-downloaded first. Prints the real error if Archive refuses."""
    params = {"q": query, "fl[]": FIELDS, "sort[]": "downloads desc", "rows": rows, "page": 1, "output": "json"}
    r = requests.get("https://archive.org/advancedsearch.php", params=params, headers=HEADERS, timeout=90)
    try:
        data = r.json()
    except Exception:
        print(f"[warn] Archive did not return JSON (status {r.status_code}): {r.text[:200]}")
        return []
    if "response" not in data:
        print(f"[warn] Archive search error (status {r.status_code}): {str(data)[:300]}")
        return []
    return data["response"]["docs"]


def search_licensed(rows_each=100):
    """Search every accepted licence URL separately, then merge and sort by downloads."""
    seen, merged = set(), []
    for url in LICENSE_URLS:
        for d in search(f'mediatype:movies AND licenseurl:"{url}"', rows_each):
            if d["identifier"] not in seen:
                seen.add(d["identifier"])
                merged.append(d)
    merged.sort(key=lambda d: int(d.get("downloads") or 0), reverse=True)
    print(f"[info] found {len(merged)} films with an accepted licence written on the page")
    return merged


def main():
    args = sys.argv[1:]
    cand = "--candidates" in args
    docs = search("collection:feature_films AND mediatype:movies", 300) if cand else search_licensed()
    shown = 0
    print(("UNVERIFIED CANDIDATES - check copyright yourself!\n" if cand else "LICENSED FILMS (licence written on the page)\n"))
    for d in docs:
        lic = (d.get("licenseurl") or "").lower()
        if not cand and not any(k in lic for k in OK_LICENSE):
            continue
        if cand and lic:
            continue              # candidates = items with no licence written
        mins = minutes(d.get("runtime") if not isinstance(d.get("runtime"), list) else d["runtime"][0])
        if "--short" in args and not (mins is not None and mins < 40):
            continue
        if "--long" in args and not (mins is not None and mins > 60):
            continue
        shown += 1
        length = f"{mins:.0f} min" if mins else "? min"
        short_lic = "BY" if "/by/" in lic else ("CC0/PD" if lic else "no licence listed")
        title = d["title"] if isinstance(d["title"], str) else d["title"][0]
        print(f"{shown:>2}. {title}\n    {int(d.get('downloads', 0)):,} downloads | {length} | {short_lic}\n"
              f"    ID: {d['identifier']}\n    https://archive.org/details/{d['identifier']}")
        if shown >= 25:
            break
    if not shown:
        print("Nothing matched. Try without --short / --long.")


if __name__ == "__main__":
    main()

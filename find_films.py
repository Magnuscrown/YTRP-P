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


def search(query, rows=200):
    params = {"q": query, "fl[]": ["identifier", "title", "downloads", "licenseurl", "runtime", "creator"],
              "sort[]": "downloads desc", "rows": rows, "page": 1, "output": "json"}
    r = requests.get("https://archive.org/advancedsearch.php", params=params, timeout=60)
    r.raise_for_status()
    return r.json()["response"]["docs"]


def main():
    args = sys.argv[1:]
    cand = "--candidates" in args
    if cand:
        q = "collection:feature_films AND mediatype:movies"
    else:
        q = ("mediatype:movies AND (licenseurl:*creativecommons.org/publicdomain* "
             "OR licenseurl:*creativecommons.org/licenses/by/*)")
    docs = search(q)
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

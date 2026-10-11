"""
EXPLAINER MAKER: one comparison video (side A vs side B) + 3 Shorts cut from the SAME script, with a FACT-CHECK before anything is rendered.

  python explainer.py                                  -> finds today's best topic (topics.py), then writes everything
  python explainer.py --topic "how to start a business with little money in 2026"

Steps: research with Google Search -> write hook + side A (fully) + side B (fully) + takeaway -> check EVERY claim with Google Search,
       fix or stop -> out/series.json with part 1 = long video, parts 2-4 = Shorts (each ends with "watch the full video").
Then run:  FORMAT=landscape python make_all.py --parts 1 --concat no     (long, horizontal)
           python make_all.py --parts 2,3,4 --concat no                  (Shorts, vertical; pictures are reused, not regenerated)
Honest limit: AI fact-checking helps a lot but is NOT perfect. Read out/factcheck.json and the script before you publish.
"""
import os, sys, json, time, argparse
from series_writer import ask_json, parse_json
from topics import grounded, best_topic, mark_used

OUT = "out"
SIDE_A = os.getenv("LABEL_A", "POOR WAY")
SIDE_B = os.getenv("LABEL_B", "RICH WAY")
DISCLAIMER = "This is general education, not financial advice."
POINTS = int(os.getenv("POINTS") or 16)      # points per side: 16 = about 10 minutes, 4 = about 3 minutes (for tests)
PER = 3                                      # beats per point


# ------------------------------------------------------------------ 1. research
def research(topic):
    text, sources = grounded(f"""Using Google Search, collect 12 accurate, specific, checkable facts for a video about:
"{topic}". Cover both sides if it is a comparison. Include numbers, rules, costs or steps where they matter, and say if something
differs by country (assume the USA unless the topic says otherwise). Do NOT include anything you cannot support.
Return JSON only: {{"facts": [{{"fact": "...", "detail": "..."}}]}}""")
    facts = parse_json(text)["facts"]
    print(f"[ok] research: {len(facts)} facts, {len(set(sources))} sources")
    return facts, sorted(set(sources))


# ------------------------------------------------------------------ 2. write the script
def write_script(topic, facts):
    fact_text = "\n".join(f"- {f['fact']} ({f.get('detail', '')})" for f in facts)
    plan = ask_json(f"""Plan a 10-minute comparison video.
TOPIC: {topic}
SIDE A is called "{SIDE_A}" (limited money, limited access, working alone). SIDE B is called "{SIDE_B}" (capital, systems, other people's help).
VERIFIED FACTS (use ONLY these for facts, numbers and rules):
{fact_text}

Return JSON: {{"title": "honest curiosity-driven title with the main search phrase, no false promises",
 "characters": [{{"name": "A", "look": "detailed look of the side A person: age, clothes, hair"}}, {{"name": "B", "look": "detailed look of the side B person"}}],
 "style": "one line art style used in every image, e.g. clean 3D cartoon, bright colours",
 "a_points": ["exactly {POINTS} short points explaining side A in order, from the very first step on"],
 "b_points": ["exactly {POINTS} short points explaining side B, matching side A point by point"]}}
Rules: respectful tone, never mock or insult people. Explain real differences in resources, systems and choices.""",
        "You are a careful explainer-video writer. Reply with JSON only.")
    a_pts, b_pts = plan["a_points"][:POINTS], plan["b_points"][:POINTS]

    def beats_for(label, points, who, role):
        out = []
        for i in range(0, len(points), 4):
            batch = points[i:i + 4]
            res = ask_json(f"""Write the narration for {len(batch)} points of a video. Side: "{label}". Main character: {who}.
CHARACTERS: {json.dumps(plan['characters'])}  STYLE: {plan['style']}
POINTS: {json.dumps(batch)}
VERIFIED FACTS (only these for facts and numbers): {fact_text}
Write exactly {PER} beats per point ({len(batch) * PER} beats), in order. Each beat: "line" = one spoken sentence of 10-16 words, simple English,
and "image" = ONE picture prompt showing exactly that line (the character, an object, a place, a clear emotion or action; no text in the picture).
{role}
Return JSON: {{"beats": [{{"line": "...", "image": "..."}}]}}""", "Reply with JSON only.")
            bs = res["beats"]
            for j, b in enumerate(bs):
                pt = i + (j * len(batch)) // max(1, len(bs))           # which point this beat belongs to
                out.append({"line": b["line"].strip(), "image": b["image"].strip(), "label": label, "pt": pt})
            time.sleep(1)
        return out

    hook = ask_json(f"""Write a 3-second hook (max 14 words) for a video titled "{plan['title']}" that names BOTH sides
("{SIDE_A}" and "{SIDE_B}") and makes people curious without lying. Also one picture prompt showing both people side by side.
Return JSON: {{"line": "...", "image": "..."}}""", "Reply with JSON only.")
    a = beats_for(SIDE_A, a_pts, plan["characters"][0]["name"],
                  "Start from the very first step. Explain it fully BEFORE the other side is mentioned.")
    b = beats_for(SIDE_B, b_pts, plan["characters"][1]["name"],
                  "Compare naturally with what side A did, but explain side B fully.")
    close = ask_json(f"""Write a 2-beat closing for the video "{plan['title']}": beat 1 = the honest takeaway (max 18 words),
beat 2 = this exact sentence: "{DISCLAIMER}". Give each a picture prompt.
Return JSON: {{"beats": [{{"line": "...", "image": "..."}}, {{"line": "...", "image": "..."}}]}}""", "Reply with JSON only.")
    hook_beat = {"line": hook["line"].strip(), "image": hook["image"].strip(), "label": "", "pt": -1}
    tail = [{"line": x["line"].strip(), "image": x["image"].strip(), "label": "", "pt": 999} for x in close["beats"]]
    return plan, hook_beat, a + b + tail


# ------------------------------------------------------------------ 3. fact-check (every claim, with search)
def check_claims(beats):
    narration = "\n".join(f"{i}: {b['line']}" for i, b in enumerate(beats))
    claims = ask_json(f"""List every FACTUAL claim in these numbered narration lines (numbers, costs, laws, rules, processes,
"always/never" statements). Skip opinions and the disclaimer. Return JSON: {{"claims": [{{"line": 0, "claim": "..."}}]}}
{narration}""", "Reply with JSON only.")["claims"]
    results, sources = [], []
    for i in range(0, len(claims), 8):
        batch = claims[i:i + 8]
        text, src = grounded(f"""Check each claim using Google Search. Be strict: if you cannot find support, say UNSURE.
Claims: {json.dumps(batch)}
Return JSON only: {{"results": [{{"line": 0, "claim": "...", "verdict": "TRUE|FALSE|UNSURE", "correction": "what is actually true, or empty"}}]}}""")
        results += parse_json(text)["results"]
        sources += src
    bad = [r for r in results if str(r.get("verdict", "")).upper() != "TRUE"]
    return results, bad, sorted(set(sources))


def fix_lines(beats, bad):
    current = {str(r["line"]): beats[int(r["line"])]["line"] for r in bad
               if str(r["line"]).isdigit() and int(r["line"]) < len(beats)}
    res = ask_json(f"""These narration lines contain claims that could NOT be verified or are wrong.
Rewrite ONLY the affected lines so they are accurate (use the correction; if there is none, remove the specific claim and keep the idea general).
Keep 10-16 words each. PROBLEMS: {json.dumps(bad)}
CURRENT LINES: {json.dumps(current)}
Return JSON: {{"fixes": [{{"line": 0, "new_line": "..."}}]}}""", "Reply with JSON only.")
    for f in res["fixes"]:
        i = int(f["line"])
        if 0 <= i < len(beats):
            beats[i]["line"] = f["new_line"].strip()


# ------------------------------------------------------------------ 4. cut the 3 Shorts from the same script
def make_shorts(plan, hook, beats, title):
    n = max(POINTS, 1)
    starts = sorted({0, n // 3, (2 * n) // 3}) if n >= 6 else [0]
    shorts = []
    for k, s in enumerate(starts[:3], 1):
        pts = {s, min(s + 1, n - 1)}
        sa = [b for b in beats if b["label"] == SIDE_A and b["pt"] in pts]
        sb = [b for b in beats if b["label"] == SIDE_B and b["pt"] in pts]
        card = {"line": "Want the full breakdown? Watch the full video on my channel.", "image": hook["image"],
                "label": "", "pt": 999}
        sbeats = [dict(hook)] + [dict(b) for b in sa + sb] + [card]
        shorts.append({"part": k + 1, "title": f"{title} (Part {k}/{len(starts[:3])}) #Shorts",
                       "narration": " ".join(b["line"] for b in sbeats), "beats": sbeats})
    return shorts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="")
    ap.add_argument("--skip-factcheck", action="store_true", help="TESTING ONLY - never publish an unchecked video")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    topic = a.topic or best_topic()["topic"]
    print(f"[topic] {topic}")
    facts, sources = research(topic)
    plan, hook, body = write_script(topic, facts)
    beats = [hook] + body

    report = {"topic": topic, "verified": False, "rounds": [], "sources": sources}
    if a.skip_factcheck:
        print("[WARNING] fact-check skipped: do NOT publish this video without checking it yourself.")
    else:
        for rnd in range(3):
            results, bad, src = check_claims(beats)
            report["rounds"].append({"checked": len(results), "problems": bad})
            report["sources"] = sorted(set(report["sources"]) | set(src))
            print(f"[factcheck] round {rnd + 1}: {len(results)} claims, {len(bad)} problems")
            if not bad:
                report["verified"] = True
                break
            if rnd == 2:
                break
            fix_lines(beats, bad)
        if not report["verified"]:
            json.dump(report, open(f"{OUT}/factcheck.json", "w"), indent=2, ensure_ascii=False)
            raise SystemExit("STOP: some claims could not be verified after 2 fixes. See out/factcheck.json. No video was made.")
    json.dump(report, open(f"{OUT}/factcheck.json", "w"), indent=2, ensure_ascii=False)

    hook, body = beats[0], beats[1:]
    long_part = {"part": 1, "title": plan["title"], "narration": " ".join(b["line"] for b in beats), "beats": beats}
    shorts = make_shorts(plan, hook, body, plan["title"])
    series = {"title": plan["title"], "style": plan["style"], "characters": plan["characters"],
              "parts": [long_part] + shorts}
    json.dump(series, open(f"{OUT}/series.json", "w"), indent=2, ensure_ascii=False)

    src_lines = "\n".join(report["sources"][:12])
    checked = f"\n\nFact-checked against sources such as:\n{src_lines}" if report["verified"] else ""
    open(f"{OUT}/titles.txt", "w").write(plan["title"])
    open(f"{OUT}/description.txt", "w").write(f"{plan['title']}\n\n{DISCLAIMER}{checked}\n")
    with open(f"{OUT}/shorts_titles.txt", "w") as f:
        f.write("\n".join(s["title"] for s in shorts))
    mark_used(topic)
    print(f"[ok] script ready: long video {len(beats)} beats (about {len(long_part['narration'].split()) / 150:.1f} min) "
          f"+ {len(shorts)} Shorts -> out/series.json")


if __name__ == "__main__":
    main()

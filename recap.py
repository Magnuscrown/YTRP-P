"""
MOVIE RECAP PIPELINE (v1) - only for films you have verified are free to reuse.

  python recap.py --id <archive.org identifier> [--confirm-public-domain] [--minutes 20] [--synopsis synopsis.txt]
  python recap.py --film my_film.mp4 --title "Film name" --license-note "Public domain (US), source: ..."   (local file)

Steps: check license -> download -> transcribe (Whisper) -> AI writes a recap per section ->
       voice (edge-tts) -> cut matching footage from the SAME section of the film -> one long video.
Outputs (folder out/): recap.mp4, description.txt, titles.txt, source.json
Needs: pip install requests edge-tts faster-whisper   and ffmpeg.   API keys as in series_writer.py
Limits of v1: it understands DIALOGUE only (no vision yet), so silent films need a synopsis file.
"""
import os, sys, re, json, math, time, argparse, subprocess, requests
from series_writer import ask_json, ask
import make_video
import find_films

OUT = "out"
TEST = os.getenv("TEST_MODE") == "1"
ENHANCE = os.getenv("ENHANCE") == "1"   # light clean-up for old footage (denoise, contrast, sharpen)
# only these licence URLs are accepted automatically (no NonCommercial, NoDerivatives or ShareAlike)
OK_LICENSE = ("creativecommons.org/publicdomain/zero", "creativecommons.org/publicdomain/mark",
              "creativecommons.org/licenses/by/")


def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", path]).strip())


# ---------------------------------------------------------------- 0. optional: pick the film automatically
def auto_pick(rank, min_minutes, max_minutes):
    """Pick the Nth most-downloaded film whose licence is WRITTEN on its Archive page (CC0 / PD mark / CC BY)."""
    good = []
    for d in find_films.search_licensed():
        lic = (d.get("licenseurl") or "").lower()
        rt = d.get("runtime")
        mins = find_films.minutes(rt[0] if isinstance(rt, list) else rt)
        if any(k in lic for k in OK_LICENSE) and mins and min_minutes <= mins <= max_minutes:
            good.append((d, mins))
    if len(good) < rank:
        raise SystemExit(f"Only {len(good)} licensed films found in that length range; try a lower pick number.")
    d, mins = good[rank - 1]
    title = d["title"] if isinstance(d["title"], str) else d["title"][0]
    print(f"[auto-pick] #{rank}: {title} ({mins:.0f} min, {int(d.get('downloads', 0)):,} downloads) id={d['identifier']}")
    return d["identifier"]


# ---------------------------------------------------------------- 1. licence check + download
def fetch(identifier, confirm_pd):
    meta = requests.get(f"https://archive.org/metadata/{identifier}", timeout=60).json()
    md = meta.get("metadata", {})
    lic = (md.get("licenseurl") or "").lower()
    title = md.get("title", identifier)
    ok = any(k in lic for k in OK_LICENSE)
    if not ok and not confirm_pd:
        raise SystemExit(
            f"STOP: '{title}' has no accepted licence on its page (licenseurl: '{lic or 'none'}').\n"
            "Only Public Domain / CC0 / CC BY are accepted automatically. If YOU have verified it is public "
            "domain (check its copyright status yourself), run again with --confirm-public-domain.")
    files = [f for f in meta.get("files", []) if f["name"].lower().endswith((".mp4", ".mkv", ".ogv", ".avi"))
             and "sample" not in f["name"].lower()]
    if not files:
        raise SystemExit("No video file found in that Internet Archive item.")
    f = max(files, key=lambda x: int(x.get("size", 0)))
    url = f"https://archive.org/download/{identifier}/{requests.utils.quote(f['name'])}"
    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/film{os.path.splitext(f['name'])[1]}"
    print(f"[download] {f['name']} ({int(f.get('size', 0)) // 1_000_000} MB)")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(path, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    note = (f"License: {lic}" if ok else "Public domain (verified by the channel owner)")
    src = {"title": title, "identifier": identifier, "page": f"https://archive.org/details/{identifier}",
           "creator": md.get("creator", ""), "license": note, "licenseurl": lic}
    return path, src


# ---------------------------------------------------------------- 2. transcript
def transcribe(film):
    cache = f"{OUT}/transcript.json"
    if os.path.exists(cache):
        return json.load(open(cache))
    from faster_whisper import WhisperModel
    wav = f"{OUT}/audio.wav"
    sh(["ffmpeg", "-y", "-i", film, "-vn", "-ac", "1", "-ar", "16000", wav])
    model = WhisperModel(os.getenv("WHISPER_MODEL", "base"), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(wav, vad_filter=True)
    data = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs]
    json.dump(data, open(cache, "w"))
    print(f"[ok] transcript: {len(data)} lines")
    return data


def make_chunks(segs, total, chunk_secs):
    n = max(1, math.ceil(total / chunk_secs))
    chunks = []
    for i in range(n):
        a, b = i * total / n, (i + 1) * total / n
        text = " ".join(s["text"] for s in segs if a <= s["start"] < b)
        chunks.append({"start": a, "end": b, "text": text})
    return chunks


# ---------------------------------------------------------------- 3. the recap script
def write_recap(chunks, title, synopsis, minutes):
    total_words = int(minutes * 150)
    film_len = chunks[-1]["end"]
    story_so_far, out = "", []
    for i, c in enumerate(chunks):
        words = max(40, int(total_words * (c["end"] - c["start"]) / film_len))
        first, last = i == 0, i == len(chunks) - 1
        role = ("Open with a gripping hook, then introduce the main characters and the situation." if first else
                "Bring the story to its ending and close with a short closing thought." if last else
                "Continue the story smoothly from the previous section.")
        res = ask_json(f"""You write ORIGINAL narration for a YouTube movie recap channel.
FILM: {title}
BACKGROUND (may help, may be incomplete): {synopsis or '(none)'}
STORY SO FAR: {story_so_far or '(this is the start)'}

DIALOGUE FROM THIS SECTION OF THE FILM (section {i+1} of {len(chunks)}):
\"\"\"{c['text'][:6000] or '(almost no dialogue in this section; rely on the background and keep it brief)'}\"\"\"

{role}
Rules: about {words} words, spoken, vivid, simple English, present tense, in your OWN words (never copy lines of dialogue).
Only describe events supported by the dialogue or background. Do not invent plot. Add a little commentary or suspense.
Return JSON: {{"narration": "...", "story_so_far": "2-3 sentence summary of everything up to the end of this section"}}""",
                       "You are a careful movie recap writer. Reply with JSON only.")
        story_so_far = res["story_so_far"]
        out.append({**c, "narration": res["narration"].strip()})
        print(f"[ok] recap section {i+1}/{len(chunks)}")
        if not TEST:
            time.sleep(2)   # be gentle with free API limits
    return out


# ---------------------------------------------------------------- 4. voice + matching footage
def cut_clips(film, a, b, need, tag):
    """Cut `need` seconds of footage from window [a, b] of the film as several ~5s shots (muted)."""
    n = max(1, round(need / 5))
    sub = need / n
    clips = []
    span = max(0.0, (b - a) - sub)
    for k in range(n):
        start = a + (span * k / (n - 1) if n > 1 else span / 2)
        clip = f"{OUT}/work/{tag}_{k}.mp4"
        sh(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", film, "-t", f"{sub:.2f}", "-an",
            "-vf", ("hqdn3d=3:2:4:3,eq=contrast=1.08:brightness=0.02:saturation=1.1,unsharp=5:5:0.7,"
                    if ENHANCE else "") +
                   "scale=1280:720:force_original_aspect_ratio=decrease,"
                   "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p", clip])
        clips.append(clip)
    return clips


def assemble(film, sections):
    os.makedirs(f"{OUT}/work", exist_ok=True)
    vids, auds, timeline, t = [], [], [], 0.0
    for i, s in enumerate(sections):
        a_path = f"{OUT}/work/voice_{i:03d}.mp3"
        make_video.make_voice(s["narration"], a_path)
        d = probe(a_path)
        vids += cut_clips(film, s["start"], s["end"], d, f"s{i:03d}")
        auds.append(a_path)
        timeline.append({"i": i, "t0": round(t, 2), "t1": round(t + d, 2), "narration": s["narration"]})
        t += d
        print(f"[ok] section {i+1}/{len(sections)} ({d:.0f}s)")
    json.dump(timeline, open(f"{OUT}/timeline.json", "w"), indent=1, ensure_ascii=False)
    for name, items in (("v", vids), ("a", auds)):
        with open(f"{OUT}/work/{name}.txt", "w") as f:
            for p in items:
                f.write(f"file '{os.path.abspath(p)}'\n")
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/work/v.txt",
        "-f", "concat", "-safe", "0", "-i", f"{OUT}/work/a.txt",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", f"{OUT}/recap.mp4"])
    print(f"Saved {OUT}/recap.mp4 ({probe(f'{OUT}/recap.mp4') / 60:.1f} min)")


# ---------------------------------------------------------------- 5. title + description
def packaging(src, sections):
    summary = " ".join(s["narration"] for s in sections)[:3000]
    try:
        t = ask_json(f"""Give 5 accurate, curiosity-driven YouTube titles for a recap of the film "{src['title']}".
No lies, no invented events. Recap text: {summary}
Return JSON: {{"titles": ["...", "..."]}}""", "Reply with JSON only.")["titles"]
    except Exception:
        t = [f"{src['title']} - Full Story Recap"]
    open(f"{OUT}/titles.txt", "w").write("\n".join(t))
    desc = (f"Recap and commentary on \"{src['title']}\".\n\n"
            f"Film source: {src.get('page', '')}\n{src['license']}\n"
            f"{'Creator: ' + src['creator'] if src.get('creator') else ''}\n\n"
            "Narration is AI-generated voice. Script written for this channel.\n")
    open(f"{OUT}/description.txt", "w").write(desc)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--id"); p.add_argument("--film"); p.add_argument("--auto", action="store_true")
    p.add_argument("--pick", type=int, default=1); p.add_argument("--min-minutes", type=float, default=60)
    p.add_argument("--max-minutes", type=float, default=180); p.add_argument("--title", default="")
    p.add_argument("--license-note", default=""); p.add_argument("--confirm-public-domain", action="store_true")
    p.add_argument("--minutes", type=float, default=20); p.add_argument("--synopsis", default="")
    p.add_argument("--chunk-seconds", type=int, default=150)
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.auto and not a.id:
        a.id = auto_pick(a.pick, a.min_minutes, a.max_minutes)
    if a.id:
        film, src = fetch(a.id, a.confirm_public_domain)
    elif a.film and a.license_note:
        film, src = a.film, {"title": a.title or os.path.basename(a.film), "license": a.license_note,
                             "page": "", "creator": ""}
    else:
        raise SystemExit("Give --id, or --auto, or --film plus --license-note.")
    json.dump(src, open(f"{OUT}/source.json", "w"), indent=2)
    synopsis = open(a.synopsis).read() if a.synopsis and os.path.exists(a.synopsis) else ""

    total = probe(film)
    segs = transcribe(film)
    words = sum(len(s["text"].split()) for s in segs)
    if words < total / 60 * 15 and not synopsis:
        print("[warn] very little dialogue found (silent film?). Results will be weak without a --synopsis file.")
    chunks = make_chunks(segs, total, a.chunk_seconds)
    sections = write_recap(chunks, src["title"], synopsis, a.minutes)
    json.dump(sections, open(f"{OUT}/recap_script.json", "w"), indent=2, ensure_ascii=False)
    assemble(film, sections)
    packaging(src, sections)


if __name__ == "__main__":
    main()

"""
STEP 2: turn one part of out/series.json into a vertical video (1080x1920)
  images (Cloudflare Workers AI, no watermark) + voice (edge-tts) + motion & captions (ffmpeg)

Run:  python make_video.py 1          (makes part 1 -> out/part_01.mp4)
Needs: pip install requests edge-tts   and ffmpeg installed
Env:   CF_ACCOUNT_ID, CF_API_TOKEN     (Cloudflare account id + API token with Workers AI access)
Test without keys:  TEST_MODE=1 python make_video.py 1   (fake images + fake voice)
"""
import os, sys, json, time, base64, subprocess, textwrap, requests

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")
CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"
TEST = os.getenv("TEST_MODE") == "1"
SHOT_SECS = float(os.getenv("SHOT_SECS") or 2.0)   # longest time before the picture cuts
# where the camera punches in on a picture (x, y as 0..1) for the extra cuts
FOCI = [(0.5, 0.25), (0.25, 0.5), (0.75, 0.5), (0.5, 0.75), (0.35, 0.3), (0.65, 0.3)]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path])
    return float(out.strip())


def make_image(prompt, path, i):
    if TEST:
        colors = ["0x234567", "0x674523", "0x456723", "0x672345"]
        run(["ffmpeg", "-y", "-f", "lavfi", "-i",
             f"color=c={colors[i % 4]}:s=1024x1024:d=1", "-frames:v", "1", path])
        return
    acc, tok = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{CF_MODEL}"
    r = None
    for attempt in range(4):
        r = requests.post(url, headers={"Authorization": f"Bearer {tok}"},
                          json={"prompt": prompt, "steps": 4}, timeout=120)
        if r.status_code == 200:
            break
        print(f"[retry] image attempt {attempt+1} failed: {r.status_code} {r.text[:150]}")
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()
    if r.headers.get("content-type", "").startswith("image/"):
        data = r.content
    else:
        data = base64.b64decode(r.json()["result"]["image"])
    with open(path, "wb") as f:
        f.write(data)


def make_voice(text, path):
    if TEST:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=220:duration=12", path])
        return
    with open(path + ".txt", "w") as f:
        f.write(text)
    subprocess.run(["edge-tts", "--voice", VOICE, "--file", path + ".txt",
                    "--write-media", path], check=True)


def split_words(text, n):
    words = text.split()
    size = max(1, -(-len(words) // n))
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)][:n]


def motion_clip(img, caption, secs, idx, out, focus=None):
    """One image -> moving clip with caption. Alternates zoom-in, zoom-out, pan left, pan right."""
    frames = int(secs * FPS)
    mode = idx % 4
    if mode == 0:    # slow zoom in
        z, x, y = "min(zoom+0.0007,1.3)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == 1:  # zoom out
        z, x, y = "if(eq(on,0),1.3,max(zoom-0.0007,1.0))", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == 2:  # pan left to right
        z, x, y = "1.25", f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
    else:            # pan right to left
        z, x, y = "1.25", f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    if focus:        # quick punch-in on one part of the picture
        fx, fy = focus
        z, x, y = "min(1.25+0.002*on,1.8)", f"(iw-iw/zoom)*{fx}", f"(ih-ih/zoom)*{fy}"
    cap_file = out + ".txt"
    with open(cap_file, "w") as f:
        f.write("\n".join(textwrap.wrap(caption, 26)))
    vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
          f"drawtext=fontfile={FONT}:textfile={cap_file}:fontsize=58:fontcolor=white:"
          f"borderw=4:bordercolor=black:line_spacing=10:x=(w-text_w)/2:y=h*0.68")
    run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-vf", vf, "-t", f"{secs:.2f}",
         "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", out])


def safe_image(prompt, path, i, last_good):
    """Make an image; if the free daily limit is hit, reuse the last good image instead of crashing."""
    try:
        make_image(prompt, path, i)
        return path
    except Exception as e:
        print(f"[warn] image failed ({str(e)[:100]}), reusing previous image")
        if last_good is None:
            raise
        return last_good


def build(part_no):
    series = json.load(open("out/series.json"))
    part = next(p for p in series["parts"] if p["part"] == part_no)
    style = series.get("style", "")
    chars = " ".join(f"{c['name']}: {c['look']}." for c in series.get("characters", []))
    work = f"out/work_{part_no:02d}"
    os.makedirs(work, exist_ok=True)

    audio = f"{work}/voice.mp3"
    make_voice(part["narration"], audio)
    total = duration(audio)

    # Build a list of beats. Old-format series (no beats) still work.
    beats = part.get("beats")
    if not beats:
        prompts = part["image_prompts"]
        caps = split_words(part["narration"], len(prompts))
        beats = [{"line": c, "image": p} for c, p in zip(caps, prompts)]

    total_words = sum(len(b["line"].split()) for b in beats) or 1
    clips, last_good, idx = [], None, 0
    for bi, beat in enumerate(beats):
        beat_secs = total * len(beat["line"].split()) / total_words
        frames = beat.get("burst") or [beat.get("image", "")]
        if len(frames) > 1:                       # action burst: quick cuts, new picture each time
            sub = max(0.4, beat_secs / len(frames))
            for fi, prompt in enumerate(frames):
                img, clip = f"{work}/img_{idx}.png", f"{work}/clip_{idx}.mp4"
                full = f"{style}. {chars} Scene: {prompt}. dynamic pose, vertical 9:16, no text, no watermark"
                last_good = safe_image(full, img, idx, last_good)
                motion_clip(last_good, beat["line"], sub, idx, clip)
                clips.append(clip)
                idx += 1
        else:                                     # normal beat: one picture, several fast punch-in cuts
            img = f"{work}/img_{idx}.png"
            full = f"{style}. {chars} Scene: {frames[0]}. dynamic pose, vertical 9:16, no text, no watermark"
            last_good = safe_image(full, img, idx, last_good)
            cuts = max(1, round(beat_secs / SHOT_SECS))
            sub = max(0.5, beat_secs / cuts)
            for k in range(cuts):
                clip = f"{work}/clip_{idx}_{k}.mp4"
                focus = None if k == 0 else FOCI[(idx + k) % len(FOCI)]
                motion_clip(last_good, beat["line"], sub, idx + k, clip, focus)
                clips.append(clip)
            idx += 1
        print(f"[ok] beat {bi+1}/{len(beats)}")

    with open(f"{work}/list.txt", "w") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    final = f"out/part_{part_no:02d}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt",
         "-i", audio, "-c:v", "copy", "-c:a", "aac", "-shortest", final])
    print(f"Saved {final} ({duration(final):.1f}s, {len(clips)} cuts from {idx} images)")


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 1)

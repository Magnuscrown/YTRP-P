"""
STEP 2: turn one part of out/series.json into a vertical video (1080x1920)
  images (Cloudflare Workers AI, no watermark) + voice (edge-tts) + motion & captions (ffmpeg)

Run:  python make_video.py 1          (makes part 1 -> out/part_01.mp4)
Needs: pip install requests edge-tts   and ffmpeg installed
Env:   CF_ACCOUNT_ID, CF_API_TOKEN     (Cloudflare account id + API token with Workers AI access)
Test without keys:  TEST_MODE=1 python make_video.py 1   (fake images + fake voice)
"""
import os, re, sys, json, time, base64, hashlib, shutil, subprocess, textwrap, requests

LANDSCAPE = os.getenv("FORMAT") == "landscape"      # long horizontal videos (16:9); default is vertical Shorts (9:16)
W, H, FPS = (1920, 1080, 30) if LANDSCAPE else (1080, 1920, 30)
UP = 1.5 if LANDSCAPE else 2      # working size for smooth zoom (smaller = faster for long videos)
SHAPE = "wide 16:9 cinematic" if LANDSCAPE else "vertical 9:16"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")
CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"
TEST = os.getenv("TEST_MODE") == "1"
SHOT_SECS = float(os.getenv("SHOT_SECS") or 2.0)   # longest time before the picture cuts
# where the camera punches in on a picture (x, y as 0..1) for the extra cuts
FOCI = [(0.5, 0.25), (0.25, 0.5), (0.75, 0.5), (0.5, 0.75), (0.35, 0.3), (0.65, 0.3)]


class DailyLimit(Exception):
    """Cloudflare's free daily image allowance is used up."""


LIMIT_HIT = False


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path])
    return float(out.strip())


_img_dead = set()      # image providers that are out of quota / failing for the rest of this run
_PW_SIZE = "width=1024&height=1024"


def _img_cloudflare(prompt):
    acc, tok = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
    r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{CF_MODEL}",
                      headers={"Authorization": f"Bearer {tok}"}, json={"prompt": prompt, "steps": 4}, timeout=120)
    if r.status_code == 429 and "daily free allocation" in r.text:
        raise DailyLimit("cloudflare daily limit")
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {r.text[:120]}")
    if r.headers.get("content-type", "").startswith("image/"):
        return r.content
    return base64.b64decode(r.json()["result"]["image"])


def _img_together(prompt):
    r = requests.post("https://api.together.xyz/v1/images/generations", timeout=120,
                      headers={"Authorization": f"Bearer {os.environ['TOGETHER_API_KEY']}"},
                      json={"model": os.getenv("TOGETHER_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell-Free"),
                            "prompt": prompt, "width": 1024, "height": 1024, "steps": 4, "n": 1,
                            "response_format": "b64_json"})
    if r.status_code == 429:
        raise DailyLimit("together rate limit")
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {r.text[:120]}")
    return base64.b64decode(r.json()["data"][0]["b64_json"])


def _img_pollinations(prompt):
    """No key needed. Rate-limited, and some outputs carry a watermark: CHECK your first images."""
    url = (f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt[:600])}"
           f"?{_PW_SIZE}&model=flux&nologo=true&seed={int(hashlib.sha1(prompt.encode()).hexdigest()[:6], 16)}")
    for attempt in range(3):
        r = requests.get(url, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
            return r.content
        if r.status_code == 429:
            time.sleep(8 * (attempt + 1))
            continue
        raise RuntimeError(f"{r.status_code}")
    raise DailyLimit("pollinations rate limit")


IMG_PROVIDERS = {"cloudflare": (_img_cloudflare, lambda: os.getenv("CF_ACCOUNT_ID") and os.getenv("CF_API_TOKEN")),
                 "together": (_img_together, lambda: os.getenv("TOGETHER_API_KEY")),
                 "pollinations": (_img_pollinations, lambda: True)}


def make_image(prompt, path, i):
    """Try each image provider in order (IMAGE_PROVIDERS, default cloudflare,together,pollinations). Out of quota -> next one."""
    if TEST:
        colors = ["0x234567", "0x674523", "0x456723", "0x672345"]
        run(["ffmpeg", "-y", "-f", "lavfi", "-i",
             f"color=c={colors[i % 4]}:s=1024x1024:d=1", "-frames:v", "1", path])
        return
    global LIMIT_HIT
    # the long video and the Shorts use the SAME pictures: one generation, reused (cache ignores 9:16 vs 16:9 wording)
    key = hashlib.sha1(prompt.replace("wide 16:9 cinematic", "").replace("vertical 9:16", "").encode()).hexdigest()
    cached = f"out/img_cache/{key}.png"
    if os.path.exists(cached):
        shutil.copy(cached, path)
        return
    order = [p.strip() for p in (os.getenv("IMAGE_PROVIDERS") or "cloudflare,together,pollinations").split(",")]
    data = None
    for name in order:
        if name in _img_dead or name not in IMG_PROVIDERS or not IMG_PROVIDERS[name][1]():
            continue
        fn = IMG_PROVIDERS[name][0]
        for attempt in range(3):
            try:
                data = fn(prompt)
                break
            except DailyLimit as e:
                print(f"[image] {name} is out of quota, switching to the next one ({str(e)[:60]})")
                _img_dead.add(name)
                break
            except Exception as e:
                print(f"[retry] image {name} attempt {attempt + 1}: {str(e)[:120]}")
                time.sleep(4 * (attempt + 1))
        else:
            print(f"[image] {name} keeps failing, switching to the next one")
            _img_dead.add(name)
        if data:
            if name != order[0] and not globals().get("_warned_" + name):
                globals()["_warned_" + name] = True
                print(f"[image] using {name} now. If its pictures show a watermark, remove it from IMAGE_PROVIDERS.")
            break
    if not data:
        LIMIT_HIT = True
        raise DailyLimit("all image providers are out of quota")
    with open(path, "wb") as f:
        f.write(data)
    os.makedirs("out/img_cache", exist_ok=True)
    shutil.copy(path, cached)


_tts_dead = set()      # voice providers that failed: not retried again in this run (saves a lot of waiting)
PIPER_VOICE = os.getenv("PIPER_VOICE", "en/en_US/ryan/high/en_US-ryan-high")
PIPER_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"


def _tts_edge(text, path):
    with open(path + ".txt", "w") as f:
        f.write(text)
    last = None
    for attempt in range(2):
        try:
            subprocess.run(["edge-tts", "--voice", VOICE, "--file", path + ".txt", "--write-media", path],
                           check=True, timeout=600, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return
        except subprocess.CalledProcessError as e:
            last = (e.stderr or b"").decode()[-200:]
            time.sleep(3)
    raise RuntimeError(f"edge-tts refused ({last.strip().splitlines()[-1] if last.strip() else 'unknown'})")


def _tts_piper(text, path):
    """Offline neural voice that runs on GitHub's own computer: no account, no limit, no blocking."""
    name = PIPER_VOICE.split("/")[-1]
    os.makedirs("models/piper", exist_ok=True)
    model = f"models/piper/{name}.onnx"
    for ext in (".onnx", ".onnx.json"):
        if not os.path.exists(f"models/piper/{name}{ext}"):
            r = requests.get(PIPER_URL + PIPER_VOICE + ext, timeout=300)
            r.raise_for_status()
            open(f"models/piper/{name}{ext}", "wb").write(r.content)
    wav = path + ".wav"
    last = ""
    for flag in ("-f", "--output_file"):
        p = subprocess.run(["python3", "-m", "piper", "-m", model, flag, wav], input=text.encode(),
                           capture_output=True, timeout=1800)
        if p.returncode == 0 and os.path.exists(wav):
            run(["ffmpeg", "-y", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "3", path])
            return
        last = p.stderr.decode()[-150:]
    raise RuntimeError(f"piper failed ({last.strip()})")


def _tts_gtts(text, path):
    """Last resort: Google Translate's voice. Works almost anywhere, but sounds more robotic."""
    from gtts import gTTS
    for attempt in range(3):
        try:
            gTTS(text=text, lang="en").save(path)
            return
        except Exception as e:
            err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"gTTS failed ({str(err)[:100]})")


VOICES = {"edge": _tts_edge, "piper": _tts_piper, "gtts": _tts_gtts}


def make_voice(text, path):
    """Voice providers in order (TTS_PROVIDERS, default edge,piper,gtts). One that fails is skipped from then on."""
    if TEST:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=220:duration=12", path])
        return
    errors = []
    for name in [p.strip() for p in (os.getenv("TTS_PROVIDERS") or "edge,piper,gtts").split(",")]:
        if name in _tts_dead or name not in VOICES:
            continue
        try:
            if os.path.exists(path):
                os.remove(path)
            VOICES[name](text, path)
            if os.path.exists(path) and os.path.getsize(path) > 2000:
                print(f"[voice] made with {name}")
                return
            raise RuntimeError("empty audio file")
        except Exception as e:
            print(f"[voice] {name} failed: {str(e)[:160]}")
            errors.append(f"{name}: {str(e)[:80]}")
            _tts_dead.add(name)
    raise SystemExit("STOP: no voice provider worked -> " + " | ".join(errors))


def split_words(text, n):
    words = text.split()
    size = max(1, -(-len(words) // n))
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)][:n]


LIVING = os.getenv("LIVING", "1") == "1"       # Level 1: handheld wobble, light flicker, film grain, soft vignette


def motion_clip(img, caption, secs, idx, out, focus=None, label=None, seq=None):
    """One picture -> moving clip with caption and a 'living' look. Alternates zoom-in, zoom-out, pan left, pan right.
    seq = [(picture, seconds), ...] shows several pictures one after another (used for small actions like a blink)."""
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
    living = ""
    if LIVING:       # tiny handheld camera shake + light that gently flickers + grain + soft dark corners
        x, y = f"({x})+9*sin(on/13)+4*sin(on/5.1)", f"({y})+9*cos(on/11)+4*cos(on/4.7)"
        living = "eq=brightness='0.012*sin(2*PI*t/2.6)':eval=frame,noise=alls=5:allf=t,vignette=PI/7,"
    cap_file = out + ".txt"
    with open(cap_file, "w") as f:
        f.write("\n".join(textwrap.wrap(caption, 44 if LANDSCAPE else 26)))
    UW, UH = int(W * UP) // 2 * 2, int(H * UP) // 2 * 2
    tail = (f"{living}drawtext=fontfile={FONT}:textfile={cap_file}:fontsize={52 if LANDSCAPE else 58}:fontcolor=white:"
            f"borderw=4:bordercolor=black:line_spacing=10:x=(w-text_w)/2:y=h*{0.78 if LANDSCAPE else 0.68}")
    if label:        # e.g. "POOR WAY" / "RICH WAY" shown at the top while that side is explained
        lab_file = out + ".label.txt"
        with open(lab_file, "w") as f:
            f.write(label)
        color = "0xE53935" if "poor" in label.lower() or "broke" in label.lower() else "0x2E7D32"
        tail += (f",drawtext=fontfile={FONT}:textfile={lab_file}:fontsize={60 if LANDSCAPE else 72}:fontcolor=white:"
                 f"box=1:boxcolor={color}@0.9:boxborderw=22:x=(w-text_w)/2:y=h*0.06")
    if seq:
        inputs, pre = [], ""
        for k, (p, d) in enumerate(seq):
            inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", p]
            pre += (f"[{k}:v]scale={UW}:{UH}:force_original_aspect_ratio=increase,crop={UW}:{UH},"
                    f"setsar=1,fps={FPS}[s{k}];")
        cat = "".join(f"[s{k}]" for k in range(len(seq))) + f"concat=n={len(seq)}:v=1:a=0[c];"
        fc = pre + cat + f"[c]zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}," + tail + "[v]"
        run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-t", f"{secs:.2f}",
             "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", out])
        return
    vf = (f"scale={UW}:{UH}:force_original_aspect_ratio=increase,crop={UW}:{UH},"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}," + tail)
    run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-vf", vf, "-t", f"{secs:.2f}",
         "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", out])


# ---------------------------------------------------------------- Level 2: small real actions (blink, raised hand...)
_edit_dead = False


def _edit_models(key):
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                     headers={"x-goog-api-key": key}, timeout=30)
    r.raise_for_status()
    names = [m["name"].replace("models/", "") for m in r.json().get("models", [])
             if "image" in m["name"] and "imagen" not in m["name"]
             and "generateContent" in m.get("supportedGenerationMethods", [])]
    def ver(n):
        mm = re.search(r"(\d+(?:\.\d+)?)", n)
        return -(float(mm.group(1)) if mm else 0)
    return sorted(names, key=lambda n: (ver(n), len(n)))[:3]


def make_edit(base_path, instruction):
    """Ask Gemini's image model to change the SAME picture a little (eyes closed, hand raised...).
    The character stays the same because the picture is edited, not redrawn. Returns the new picture's path or None."""
    global _edit_dead
    key = os.getenv("GEMINI_API_KEY")
    if _edit_dead or not key or TEST and not os.getenv("TEST_EDIT"):
        return None
    raw = open(base_path, "rb").read()
    cached = f"out/img_cache/edit_{hashlib.sha1(raw + instruction.encode()).hexdigest()}.png"
    if os.path.exists(cached):
        return cached
    prompt = ("Edit this image. Keep the SAME character, same art style, same background, same colors and the same camera "
              f"framing exactly. Change only this one small thing: {instruction}. Do not add any text or watermark.")
    try:
        for model in _edit_models(key):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                              headers={"x-goog-api-key": key}, timeout=120,
                              json={"contents": [{"parts": [{"inline_data": {"mime_type": "image/png",
                                                                             "data": base64.b64encode(raw).decode()}},
                                                            {"text": prompt}]}],
                                    "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}})
            if r.status_code == 429:
                break
            if r.status_code != 200:
                print(f"[edit] {model}: {r.status_code} {r.text[:100]}")
                continue
            for part in r.json()["candidates"][0]["content"]["parts"]:
                d = part.get("inlineData") or part.get("inline_data")
                if d and d.get("data"):
                    os.makedirs("out/img_cache", exist_ok=True)
                    with open(cached, "wb") as f:
                        f.write(base64.b64decode(d["data"]))
                    print(f"[edit] made an action picture with {model}: {instruction[:50]}")
                    return cached
        print("[edit] no action picture this time; using the normal picture")
    except Exception as e:
        print(f"[edit] failed ({str(e)[:100]})")
    _edit_dead = True       # quota or unsupported: stop asking for the rest of the run
    return None


def safe_image(prompt, path, i, last_good):
    """Make an image. If the free daily limit is hit mid-video, reuse the last good image."""
    try:
        make_image(prompt, path, i)
        return path
    except DailyLimit:
        if last_good is None:
            raise SystemExit("STOP: every image provider is out of quota (Cloudflare resets daily). "
                             "Add a TOGETHER_API_KEY secret for a second source, or try again later.")
        print("[warn] daily image limit hit, reusing previous image")
        return last_good
    except Exception as e:
        print(f"[warn] image failed ({str(e)[:100]}), reusing previous image")
        if last_good is None:
            raise
        return last_good


def images_needed(part):
    """How many NEW images this part will generate."""
    beats = part.get("beats")
    if not beats:
        return len(part.get("image_prompts", []))
    return sum(len(b.get("burst") or [1]) for b in beats if not b.get("same_as_prev"))


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
                full = f"{style}. {chars} Scene: {prompt}. dynamic pose, {SHAPE}, no text, no watermark"
                last_good = safe_image(full, img, idx, last_good)
                motion_clip(last_good, beat["line"], sub, idx, clip, None, beat.get("label"))
                clips.append(clip)
                idx += 1
        else:                                     # normal beat: one picture, several fast punch-in cuts
            img = f"{work}/img_{idx}.png"
            full = f"{style}. {chars} Scene: {frames[0]}. dynamic pose, {SHAPE}, no text, no watermark"
            if not (beat.get("same_as_prev") and last_good):      # a beat may reuse the previous picture (saves images)
                last_good = safe_image(full, img, idx, last_good)
            edited = make_edit(last_good, beat["edit"]) if beat.get("edit") and last_good else None
            if edited:                            # small real action: picture -> changed picture -> picture
                T = beat_secs
                d1, d2 = T * 0.45, min(0.9, T * 0.22)
                clip = f"{work}/clip_{idx}_act.mp4"
                motion_clip(None, beat["line"], T, idx, clip, None, beat.get("label"),
                            seq=[(last_good, d1), (edited, d2), (last_good, max(0.2, T - d1 - d2))])
                clips.append(clip)
            else:
                cuts = max(1, round(beat_secs / SHOT_SECS))
                sub = max(0.5, beat_secs / cuts)
                for k in range(cuts):
                    clip = f"{work}/clip_{idx}_{k}.mp4"
                    focus = None if k == 0 else FOCI[(idx + k) % len(FOCI)]
                    motion_clip(last_good, beat["line"], sub, idx + k, clip, focus, beat.get("label"))
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

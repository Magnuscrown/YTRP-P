"""
THUMBNAIL MAKER: picks the 3 best-looking frames from out/recap.mp4 and adds a short, honest headline.
  python thumbnail.py            -> out/thumbnails/thumb_1.jpg, thumb_2.jpg, thumb_3.jpg  (1280x720)
  python thumbnail.py --video out/recap.mp4 --headline "THE LAST NIGHT"
Needs: pip install pillow requests   and ffmpeg.   Headline words come from the AI (keys as in series_writer.py).
"""
import os, sys, json, argparse, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageStat

OUT = "out"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 1280, 720


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "default=nw=1:nk=1", p]).strip())


def sample_frames(video, n=36):
    d = duration(video)
    os.makedirs(f"{OUT}/thumbnails/frames", exist_ok=True)
    frames = []
    for i in range(n):
        t = d * (0.05 + 0.9 * i / (n - 1))
        path = f"{OUT}/thumbnails/frames/f{i:02d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", path], check=True)
        frames.append((t, path))
    return frames


def score(path):
    """Higher = sharper, more contrast, not too dark / washed out."""
    im = Image.open(path).convert("L").resize((320, 180))
    edges = ImageStat.Stat(im.filter(ImageFilter.FIND_EDGES))
    st = ImageStat.Stat(im)
    sharp, contrast, bright = edges.var[0] ** 0.5, st.stddev[0], st.mean[0]
    penalty = 0
    if bright < 50: penalty += (50 - bright) * 1.5
    if bright > 190: penalty += (bright - 190) * 1.5
    return sharp * 0.6 + contrast * 0.8 - penalty


def pick_best(frames, k=3, min_gap=60):
    ranked = sorted(frames, key=lambda f: score(f[1]), reverse=True)
    chosen = []
    for t, p in ranked:
        if all(abs(t - t2) >= min_gap for t2, _ in chosen):
            chosen.append((t, p))
        if len(chosen) == k:
            break
    for t, p in ranked:                      # short videos: fill up if gap rule was too strict
        if len(chosen) == k:
            break
        if (t, p) not in chosen:
            chosen.append((t, p))
    return chosen


def headlines(title, text):
    try:
        from series_writer import ask_json
        res = ask_json(f"""Write 3 YouTube thumbnail headlines for a movie recap video.
Title: {title}
Recap text: {text[:2500]}
Rules: 2 to 4 words each, ALL CAPS, curiosity-driven, and TRUE to the story (no invented events).
Return JSON: {{"headlines": ["...", "...", "..."]}}""", "Reply with JSON only.")
        hs = [h.strip().upper() for h in res["headlines"] if h.strip()]
        if hs:
            return hs
    except Exception as e:
        print(f"[warn] AI headline failed ({str(e)[:80]}), using the title")
    return [" ".join(title.upper().split()[:4])]


def fit_text(draw, text, max_w, max_lines=2):
    for size in range(150, 50, -6):
        font = ImageFont.truetype(FONT, size)
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= max_lines and all(draw.textlength(l, font=font) <= max_w for l in lines):
            return font, lines
    return ImageFont.truetype(FONT, 50), text.split()[:2]


def render(frame_path, headline, out):
    im = Image.open(frame_path).convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.35)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    # dark gradient at the bottom so the text is readable on any picture
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.35) / (H * 0.65)) ** 1.4 * 235))
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.composite(shade, im, grad.resize((W, H)))
    d = ImageDraw.Draw(im)
    font, lines = fit_text(d, headline, W - 120)
    lh = font.size * 1.08
    y = H - 50 - lh * len(lines)
    for i, line in enumerate(lines):
        x = 60
        color = (255, 214, 0) if i == len(lines) - 1 else (255, 255, 255)
        d.text((x, y + i * lh), line, font=font, fill=color, stroke_width=9, stroke_fill=(0, 0, 0))
    im.save(out, "JPEG", quality=90, optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default=f"{OUT}/recap.mp4")
    ap.add_argument("--headline", default="")
    a = ap.parse_args()
    title = "Movie recap"
    if os.path.exists(f"{OUT}/titles.txt"):
        title = open(f"{OUT}/titles.txt").read().split("\n")[0] or title
    elif os.path.exists(f"{OUT}/source.json"):
        title = json.load(open(f"{OUT}/source.json")).get("title", title)
    text = ""
    if os.path.exists(f"{OUT}/recap_script.json"):
        text = " ".join(s["narration"] for s in json.load(open(f"{OUT}/recap_script.json")))
    hs = [a.headline] if a.headline else headlines(title, text)
    best = pick_best(sample_frames(a.video))
    os.makedirs(f"{OUT}/thumbnails", exist_ok=True)
    for i, (t, p) in enumerate(best, 1):
        out = render(p, hs[(i - 1) % len(hs)], f"{OUT}/thumbnails/thumb_{i}.jpg")
        print(f"[ok] {out} (frame at {t:.0f}s, headline: {hs[(i - 1) % len(hs)]}, {os.path.getsize(out) // 1000} KB)")


if __name__ == "__main__":
    main()

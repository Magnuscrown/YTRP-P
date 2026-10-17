"""Thumbnail maker: big expressive stickman faces, huge high-contrast text, curiosity wording.
Long videos get 1280x720. Shorts get 1080x1920 (use it as the cover if you set one on desktop).
Layouts rotate (split POOR vs RICH, big face left/right) and colors change per video."""
import random
import re

import numpy as np
from PIL import Image, ImageDraw

import rig
from draw import Ctx, font
from formats import FORMATS

SS = 2
YELLOW, WHITE, INK = (255, 225, 40), (255, 255, 255), (15, 15, 20)
RED, GREEN = (226, 50, 50), (40, 180, 80)

PALETTES = [  # (top, bottom, burst, shirt)
    ((20, 30, 95), (5, 8, 40), (38, 55, 150), rig.SHIRT_RED),
    ((70, 20, 120), (22, 5, 55), (110, 45, 180), rig.SHIRT_GREEN),
    ((35, 5, 5), (130, 15, 15), (170, 30, 30), rig.SHIRT_BLUE),
    ((10, 70, 60), (3, 25, 28), (20, 120, 100), rig.SHIRT_RED),
]


# ------------------------------------------------------------------ helpers
def _grad(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - t) + np.array(bot)[None, None, :] * t
    return Image.fromarray(np.broadcast_to(arr, (h, w, 3)).astype(np.uint8))


def _panel(w, h, top, bot, burst, rays=18, cx=0.5, cy=0.5):
    """Gradient with a sunburst of rays behind the face."""
    import math
    img = _grad(w, h, top, bot)
    d = ImageDraw.Draw(img)
    ox, oy, R = w * cx, h * cy, max(w, h) * 1.6
    for i in range(0, rays * 2, 2):
        a0, a1 = math.radians(i * 180 / rays), math.radians((i + 1) * 180 / rays)
        d.polygon([(ox, oy), (ox + R * math.cos(a0), oy + R * math.sin(a0)), (ox + R * math.cos(a1), oy + R * math.sin(a1))], fill=burst)
    return img


def _splits(words, k):
    from itertools import combinations
    best = None
    for cuts in combinations(range(1, len(words)), k - 1):
        idx = (0,) + cuts + (len(words),)
        lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(k)]
        score = max(len(l) for l in lines)
        if best is None or score < best[0]:
            best = (score, lines)
    return best[1]


def _fit(text, max_w, max_h, max_px):
    words = text.split()
    best = None
    for k in (1, 2, 3):
        if k > len(words):
            break
        lines = [text] if k == 1 else _splits(words, k)
        px = int(max_px)
        while px > 24:
            f = font(px)
            w = max(f.getbbox(l)[2] - f.getbbox(l)[0] for l in lines)
            if w <= max_w and len(lines) * px * 1.08 <= max_h:
                break
            px = int(px * 0.94)
        if best is None or px > best[0]:
            best = (px, lines)
    return best


def _line_color(line):
    up = line.upper()
    if "POOR" in up or "BROKE" in up:
        return (255, 80, 80)
    if "RICH" in up:
        return (90, 240, 120)
    return YELLOW


def _text_block(d, text, box, max_px, align="center"):
    """Draws huge stroked text fitted inside box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    px, lines = _fit(text.upper(), x1 - x0, y1 - y0, max_px)
    lh = px * 1.08
    top = (y0 + y1) / 2 - lh * len(lines) / 2 + lh / 2
    sw = max(4, int(px * 0.09))
    f = font(px)
    for i, ln in enumerate(lines):
        y = top + i * lh
        x = (x0 + x1) / 2 if align == "center" else x0
        anchor = "mm" if align == "center" else "lm"
        d.text((x + px * 0.04, y + px * 0.07), ln, font=f, fill=(0, 0, 0), anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0))
        d.text((x, y), ln, font=f, fill=_line_color(ln), anchor=anchor, stroke_width=sw, stroke_fill=INK)


def _ribbon(d, cx, cy, text, px, fill, ink=WHITE):
    f = font(px)
    w = f.getbbox(text)[2] - f.getbbox(text)[0]
    pad = px * 0.55
    d.rounded_rectangle((cx - w / 2 - pad, cy - px * 0.8, cx + w / 2 + pad, cy + px * 0.8), radius=px * 0.4, fill=fill, outline=INK, width=max(3, int(px * 0.12)))
    d.text((cx, cy), text, font=f, fill=ink, anchor="mm", stroke_width=max(2, int(px * 0.05)), stroke_fill=INK)


def _figure(img, cx, head_cy, size, emo, shirt, action, col=(20, 20, 28)):
    """Draws a stickman so that the HEAD CENTER lands exactly at (cx, head_cy). Legs are cropped by the frame."""
    c = Ctx(img)
    old = rig.LW
    rig.LW = 0.030            # thick cartoon outline for thumbnails
    try:
        p = rig.pose_at(action, 1.0)
        p["jump"] = 0.0
        p["dx"] = 0.0
        k = rig.skeleton(p)
        foot = max(k["fa"][1], k["fb"][1])
        gx = cx - k["head"][0] * size
        gy = head_cy - (-foot + k["head"][1]) * size
        c.push(gx, gy, size)
        rig.draw_stick(c, p, emo, 1.0, col, extras=False, shirt=shirt)
        c.pop()
    finally:
        rig.LW = old


# ------------------------------------------------------------------ text ideas
def _thumb_text(job, rnd, script=""):
    F = FORMATS.get(job.get("fmt"), FORMATS["countdown"])
    fallback = rnd.choice(F["thumb"])
    try:
        from llm import ask
        words = (script or "").split()
        excerpt = ""
        if words:
            excerpt = ("\nScript opening: " + " ".join(words[:90]) +
                       "\nScript ending part: " + " ".join(words[-140:-40] if len(words) > 200 else words[-90:]))
        prompt = (f'Video title: "{job["title"]}"{excerpt}\n'
                  "Find the single most shocking, surprising or uncomfortable idea in this video and turn it into 4 thumbnail texts. "
                  "Rules: 2 to 4 words, ALL CAPS, max 24 characters, each must create a curiosity gap or a small sting, "
                  "like: YOU DO THIS, THE RICH HIDE THIS, STOP DOING THIS, THE LAST ONE HURTS. "
                  "Base it on what is really in the script, but do NOT give away the answer. Do NOT repeat the title. "
                  "No quotes, no emojis, no full sentences. One per line, nothing else.")
        raw = ask(prompt, max_tokens=80, temperature=0.9, validate=lambda t: len(t.strip().splitlines()) >= 2)
        opts = []
        for ln in raw.splitlines():
            ln = re.sub(r"^[\s\-\d.)*\"']+|[\"'\s]+$", "", ln).upper()
            if 2 <= len(ln.split()) <= 4 and len(ln) <= 24 and re.fullmatch(r"[A-Z0-9 ,.'!?#$%&-]+", ln):
                opts.append(ln)
        if opts:
            return rnd.choice(opts)
    except Exception:
        pass
    return fallback


# ------------------------------------------------------------------ layouts
def _split(img, W, H, text, rnd):
    half = W // 2
    left = _panel(half, H, (45, 55, 85), (12, 16, 36), (62, 76, 118), cx=0.5, cy=0.45)
    right = _panel(W - half, H, (255, 205, 40), (255, 140, 20), (255, 225, 90), cx=0.5, cy=0.45)
    img.paste(left, (0, 0))
    img.paste(right, (half, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((half - W * 0.006, 0, half + W * 0.006, H), fill=WHITE)
    size = 1.0 * H
    _figure(img, W * 0.25, H * 0.45, size, rnd.choice(["shocked", "shocked", "worried"]), rig.SHIRT_RED, rnd.choice(["scared", "facepalm"]))
    _figure(img, W * 0.75, H * 0.45, size, rnd.choice(["confident", "laughing", "happy"]), rig.SHIRT_GREEN, rnd.choice(["celebrate", "point"]))
    d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - H * 0.085, H * 0.45 - H * 0.085, W / 2 + H * 0.085, H * 0.45 + H * 0.085), fill=WHITE, outline=INK, width=int(H * 0.012))
    d.text((W / 2, H * 0.45), "VS", font=font(int(H * 0.09)), fill=INK, anchor="mm")
    _ribbon(d, W * 0.2, H * 0.08, "POOR", int(H * 0.07), RED)
    _ribbon(d, W * 0.8, H * 0.08, "RICH", int(H * 0.07), GREEN)
    _text_block(d, text, (W * 0.04, H * 0.77, W * 0.96, H * 0.98), H * 0.22)


def _face(img, W, H, text, rnd, mirror):
    top, bot, burst, shirt = rnd.choice(PALETTES)
    fx = 0.27 if mirror else 0.73
    bg = _panel(W, H, top, bot, burst, cx=fx, cy=0.45)
    img.paste(bg, (0, 0))
    emo = rnd.choice(["shocked", "shocked", "shocked", "worried"])
    _figure(img, W * fx, H * 0.47, 1.28 * H, emo, shirt, rnd.choice(["scared", "facepalm", "think"]))
    d = ImageDraw.Draw(img)
    tx0, tx1 = (W * 0.50, W * 0.97) if mirror else (W * 0.03, W * 0.52)
    _text_block(d, text, (tx0, H * 0.10, tx1, H * 0.78), H * 0.30)
    _ribbon(d, (tx0 + tx1) / 2, H * 0.90, "RICH vs POOR", int(H * 0.065), RED if not mirror else GREEN)


def _stack(img, W, H, text, rnd):
    top, bot, burst, shirt = rnd.choice(PALETTES)
    img.paste(_panel(W, H, top, bot, burst, cx=0.5, cy=0.56), (0, 0))
    emo = rnd.choice(["shocked", "shocked", "worried"])
    _figure(img, W * 0.5, H * 0.58, 1.75 * W, emo, shirt, rnd.choice(["scared", "facepalm"]))
    d = ImageDraw.Draw(img)
    _text_block(d, text, (W * 0.05, H * 0.04, W * 0.95, H * 0.27), W * 0.30)
    _ribbon(d, W * 0.5, H * 0.93, "RICH vs POOR", int(W * 0.075), RED)


# ------------------------------------------------------------------ public
def make_thumbnail(job, out_path, seed=None, script=""):
    """Creates the thumbnail JPG for a job. The text comes from the script itself. Returns the thumbnail text used."""
    rnd = random.Random(seed if seed is not None else job["title"])
    portrait = job.get("kind") == "short"
    W, H = (1080, 1920) if portrait else (1280, 720)
    text = _thumb_text(job, rnd, script)
    img = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
    if portrait:
        _stack(img, W * SS, H * SS, text, rnd)
    else:
        layout = rnd.choice(["split", "face", "face_mirror"])
        if layout == "split":
            _split(img, W * SS, H * SS, text, rnd)
        else:
            _face(img, W * SS, H * SS, text, rnd, mirror=(layout == "face_mirror"))
    img = img.resize((W, H), Image.LANCZOS)
    q = 92
    while True:
        img.save(out_path, "JPEG", quality=q, optimize=True)
        import os
        if os.path.getsize(out_path) < 1_900_000 or q <= 60:
            break
        q -= 8
    print(f"[thumb] {out_path} text='{text}'")
    return text

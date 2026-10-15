"""Ken Burns + varied transitions, synced to the voiceover. Output: H.264 yuv420p MP4."""
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):          # MoviePy 1.0.3 + Pillow 10 patch
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import functools
import random
import subprocess

import numpy as np
from PIL import Image
from moviepy.editor import VideoClip, CompositeVideoClip, AudioFileClip

from config import FPS

FADE, SLIDE, DIP = 0.35, 0.45, 0.30


@functools.lru_cache(maxsize=12)
def _load(path):
    return Image.open(path).convert("RGB")


def make_effect(name, rng):
    """Returns p(0..1) -> (zoom, fx, fy). fx/fy = where the window sits inside the free space."""
    cx, cy = rng.uniform(0.35, 0.65), rng.uniform(0.35, 0.65)
    sx, sy = rng.choice([True, False]), rng.choice([True, False])
    lerp = lambda a, b, p: a + (b - a) * p
    return {
        "zoom_in":  lambda p: (1 + 0.15 * p, cx, cy),
        "zoom_out": lambda p: (1.15 - 0.15 * p, cx, cy),
        "pan_left":  lambda p: (1.12, lerp(.75, .25, p), cy),
        "pan_right": lambda p: (1.12, lerp(.25, .75, p), cy),
        "pan_up":    lambda p: (1.12, cx, lerp(.75, .25, p)),
        "pan_down":  lambda p: (1.12, cx, lerp(.25, .75, p)),
        "diag_in":  lambda p: (1 + 0.15 * p, lerp(.3, .7, p) if sx else lerp(.7, .3, p), lerp(.3, .7, p) if sy else lerp(.7, .3, p)),
        "diag_out": lambda p: (1.15 - 0.15 * p, lerp(.3, .7, p) if sx else lerp(.7, .3, p), lerp(.3, .7, p) if sy else lerp(.7, .3, p)),
    }[name]


EFFECTS = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down", "diag_in", "diag_out"]
EFFECT_W = [3, 3, 2, 2, 1, 1, 2, 2]
TRANSITIONS = ["cut", "fade", "dip", "slide_l", "slide_u"]
TRANS_W = [4, 4, 1, 2, 2]


def kb_frame(path, effect, d, W, H):
    def frame(t):
        img = _load(path)
        Sw, Sh = img.size
        p = min(max(t / d, 0.0), 1.0)
        z, fx, fy = effect(p)
        if Sw / Sh > W / H:
            wh, ww = Sh, Sh * W / H
        else:
            ww, wh = Sw, Sw * H / W
        ww, wh = ww / z, wh / z
        x0 = min(max((Sw - ww) * fx, 0.0), Sw - ww)
        y0 = min(max((Sh - wh) * fy, 0.0), Sh - wh)
        x0, y0 = max(x0, 0.0), max(y0, 0.0)
        box = (x0, y0, min(x0 + ww, Sw), min(y0 + wh, Sh))
        return np.asarray(img.resize((W, H), Image.BILINEAR, box=box))
    return frame


def _plan(scenes, rng):
    prev_eff, prev_tr, prev_key = None, None, None
    for i, sc in enumerate(scenes):
        while True:
            eff = rng.choices(EFFECTS, EFFECT_W)[0]
            if eff != prev_eff:
                break
        tr = "cut" if i == 0 else rng.choices(TRANSITIONS, TRANS_W)[0]
        if tr == prev_tr and tr != "cut":
            tr = "cut"
        if sc["key"] == prev_key:
            tr = "cut"                      # same image twice in a row: punch-in cut with a new move
        sc["eff"], sc["tr"] = eff, tr
        prev_eff, prev_tr, prev_key = eff, tr, sc["key"]


def render_video(scenes, audio_path, size, out_path, fps=FPS, seed=None):
    W, H = size
    rng = random.Random(seed)
    _plan(scenes, rng)
    audio = AudioFileClip(audio_path)
    total = audio.duration
    clips = []
    n = len(scenes)
    for i, sc in enumerate(scenes):
        t0, d = sc["start"], sc["dur"]
        tr = sc["tr"]
        nxt = scenes[i + 1]["tr"] if i + 1 < n else "cut"
        tail = DIP if nxt == "dip" else 0.0
        ext = {"fade": FADE, "slide_l": SLIDE, "slide_u": SLIDE}.get(nxt, 0.0)
        base = kb_frame(sc["path"], make_effect(sc["eff"], rng), d, W, H)

        def f(t, base=base, d=d, tr=tr, tail=tail):
            im = base(t)
            if tr == "dip" and t < DIP:
                im = (im * (t / DIP)).astype(np.uint8)
            if tail and t > d - tail:
                im = (im * max(0.0, (d - t) / tail)).astype(np.uint8)
            return im

        dur = d + ext
        if tr in ("fade", "slide_l", "slide_u"):
            hl = min(FADE if tr == "fade" else SLIDE, d * 0.5)
            head = VideoClip(f, duration=hl).set_start(t0)
            if tr == "fade":
                mask = VideoClip(lambda t, hl=hl: np.full((H, W), min(1.0, t / hl)), ismask=True, duration=hl)
                head = head.set_mask(mask)
            else:
                def pos(t, hl=hl, tr=tr):
                    u = 1 - min(1.0, t / hl)
                    e = u ** 3
                    return (int(W * e), 0) if tr == "slide_l" else (0, int(H * e))
                head = head.set_position(pos)
            body = VideoClip(lambda t, f=f, hl=hl: f(t + hl), duration=dur - hl).set_start(t0 + hl)
            clips += [head, body]
        else:
            clips.append(VideoClip(f, duration=dur).set_start(t0))

    video = CompositeVideoClip(clips, size=(W, H), bg_color=(0, 0, 0)).set_duration(total).set_audio(audio)
    video.write_videofile(
        str(out_path), fps=fps, codec="libx264", audio_codec="aac", preset="veryfast", threads=4,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-profile:v", "baseline", "-level", "4.0", "-movflags", "+faststart"],
        logger="bar",
    )
    audio.close()
    return probe_duration(out_path)


def probe_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=nw=1:nk=1", str(path)], capture_output=True, text=True).stdout
        return float(out.strip())
    except Exception:
        return 0.0

"""Assembles animated stickman scenes with varied transitions, synced to the voiceover."""
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):          # MoviePy 1.0.3 + Pillow 10 patch
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import random
import subprocess

import numpy as np
from moviepy.editor import VideoClip, CompositeVideoClip, AudioFileClip

from config import FPS
from stage import make_scene_frame

FADE, SLIDE, DIP = 0.35, 0.45, 0.30
TRANSITIONS = ["cut", "fade", "dip", "slide_l", "slide_u"]
TRANS_W = [4, 4, 1, 2, 2]


def _plan(scenes, rng):
    prev = None
    for i, sc in enumerate(scenes):
        tr = "cut" if i == 0 else rng.choices(TRANSITIONS, TRANS_W)[0]
        if tr == prev and tr != "cut":
            tr = "cut"
        sc["tr"] = tr
        prev = tr


def render_video(scenes, audio_path, size, out_path, fps=FPS, seed=None):
    W, H = size
    rng = random.Random(seed)
    _plan(scenes, rng)
    audio = AudioFileClip(audio_path)
    total = audio.duration
    clips, n = [], len(scenes)
    for i, sc in enumerate(scenes):
        t0, d, tr = sc["start"], sc["dur"], sc["tr"]
        nxt = scenes[i + 1]["tr"] if i + 1 < n else "cut"
        tail = DIP if nxt == "dip" else 0.0
        ext = {"fade": FADE, "slide_l": SLIDE, "slide_u": SLIDE}.get(nxt, 0.0)
        base = make_scene_frame(sc, W, H)

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
                head = head.set_mask(VideoClip(lambda t, hl=hl: np.full((H, W), min(1.0, t / hl)), ismask=True, duration=hl))
            else:
                def pos(t, hl=hl, tr=tr):
                    e = (1 - min(1.0, t / hl)) ** 3
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
        logger="bar")
    audio.close()
    return probe_duration(out_path)


def probe_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                              "default=nw=1:nk=1", str(path)], capture_output=True, text=True).stdout
        return float(out.strip())
    except Exception:
        return 0.0

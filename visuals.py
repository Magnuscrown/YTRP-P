"""Cloudflare Workers AI (flux-1-schnell). One image per unique key; failures reuse nearby images."""
import base64
import hashlib
import io
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image, ImageStat

from config import CF_ACCOUNT_ID, CF_API_TOKEN, CF_IMAGE_MODEL, IMAGE_WORKERS

URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_IMAGE_MODEL}"
COMPOSITIONS = ["wide establishing shot", "close-up shot", "medium shot", "over-the-shoulder shot",
                "low angle shot", "high angle shot", "aerial view", "shallow depth of field",
                "symmetrical framing", "rule of thirds composition"]
LIGHTING = ["golden hour light", "soft morning light", "moody noir lighting", "blue hour dusk",
            "warm window light", "dramatic side lighting", "neon city glow", "overcast soft light",
            "late night desk lamp", "bright clean daylight", "candlelit warm tones",
            "rim lighting", "foggy diffused light", "sunset backlight"]
STYLE = ("2D animated cartoon style, flat vibrant colors, clean bold outlines, modern explainer-video animation, "
         "detailed background, no text, no letters, no watermark, no logo")
QUOTA_HIT = threading.Event()


def build_prompt(visual, key):
    rng = random.Random(key)
    return f"{visual}, {rng.choice(COMPOSITIONS)}, {rng.choice(LIGHTING)}, {STYLE}"[:1500]


def _good(img):
    st = ImageStat.Stat(img)
    return sum(st.stddev) / 3 > 8        # rejects solid navy / black placeholders


def _gen_one(prompt, path):
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    for attempt in range(4):
        if QUOTA_HIT.is_set():
            return False
        try:
            r = requests.post(URL, headers=headers, timeout=120,
                              json={"prompt": prompt + (", sharp focus" if attempt else ""), "steps": 4})
            if r.status_code == 200:
                if r.headers.get("content-type", "").startswith("image"):
                    raw = r.content
                else:
                    raw = base64.b64decode((r.json().get("result") or {}).get("image", ""))
                img = Image.open(io.BytesIO(raw)).convert("RGB")
                if _good(img):
                    img.save(path, "JPEG", quality=92)
                    return True
            else:
                body = r.text.lower()
                if r.status_code == 429 and ("neuron" in body or "daily" in body or "quota" in body):
                    QUOTA_HIT.set()
                    print("[images] Cloudflare daily limit reached; reusing existing images for the rest")
                    return False
                time.sleep(4 * (attempt + 1))
        except Exception:
            time.sleep(3 * (attempt + 1))
    return False


def generate(visuals, out_dir):
    """visuals: {key: description}. Returns {key: path or None}."""
    out_dir = Path(out_dir)
    paths = {}

    def job(item):
        key, vis = item
        p = out_dir / f"img_{hashlib.md5(key.encode()).hexdigest()[:10]}.jpg"
        ok = _gen_one(build_prompt(vis, key), p)
        return key, (str(p) if ok else None)

    with ThreadPoolExecutor(IMAGE_WORKERS) as ex:
        for key, p in ex.map(job, visuals.items()):
            paths[key] = p
    good = sum(1 for p in paths.values() if p)
    print(f"[images] {good}/{len(paths)} generated")
    return paths


def resolve_paths(scenes, key_paths):
    """Gives every scene an image; a missing one borrows the nearest good image (never a blank frame)."""
    last = None
    for sc in scenes:
        p = key_paths.get(sc["key"])
        if p:
            last = p
        sc["path"] = p or last
    first_good = next((sc["path"] for sc in scenes if sc["path"]), None)
    if not first_good:
        raise RuntimeError("No images could be generated")
    for sc in scenes:
        sc["path"] = sc["path"] or first_good

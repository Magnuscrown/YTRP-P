"""Cuts the narration into 3-5 second scenes and plans one image per scene.
Scenes that repeat an earlier visual idea reuse that exact image (different zoom/transition)."""
import json
import math
import random
import re

from llm import ask
from config import SCENE_MIN_SEC, SCENE_MAX_SEC

BATCH = 30


def build_scenes(sentences, durations, rng=None):
    rng = rng or random.Random()
    units = []
    for s, d in zip(sentences, durations):
        w = s.split()
        if d > SCENE_MAX_SEC + 0.5 and len(w) > 1:
            n = min(math.ceil(d / 4.4), len(w))
            size = len(w) / n
            for k in range(n):
                part = w[round(k * size):round((k + 1) * size)]
                if part:
                    units.append((" ".join(part), d * len(part) / len(w)))
        else:
            units.append((s, d))
    scenes, acc, acc_d, t = [], [], 0.0, 0.0
    target = rng.uniform(3.2, 4.8)

    def close():
        nonlocal acc, acc_d, t, target
        scenes.append({"text": " ".join(acc), "start": t, "dur": acc_d})
        t += acc_d
        acc, acc_d, target = [], 0.0, rng.uniform(3.2, 4.8)

    for text, d in units:
        if acc and acc_d + d > SCENE_MAX_SEC + 0.2 and acc_d >= 2.5:
            close()
        acc.append(text)
        acc_d += d
        if acc_d >= target:
            close()
    if acc:
        if acc_d < 1.5 and scenes:
            scenes[-1]["text"] += " " + " ".join(acc)
            scenes[-1]["dur"] += acc_d
        else:
            close()
    return scenes


def _norm_key(k):
    return re.sub(r"[^a-z0-9 ]", "", str(k).lower()).strip()


def _closest(key, keys):
    kw = set(key.split())
    best, score = keys[-1], -1.0
    for k in keys:
        s = len(kw & set(k.split())) / max(1, len(kw | set(k.split())))
        if s >= score:
            best, score = k, s
    return best


def _parse(raw):
    raw = re.sub(r"```(json)?", "", raw)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except Exception:
        try:
            data = json.loads(re.sub(r",\s*([\]}])", r"\1", m.group(0)))
        except Exception:
            return None
    return [d for d in data if isinstance(d, dict) and "i" in d and "key" in d]


def plan_visuals(scenes, topic, max_images):
    """Fills scene['key']; returns {key: visual description}."""
    visuals, keys = {}, []
    n = len(scenes)
    for b0 in range(0, n, BATCH):
        batch = scenes[b0:b0 + BATCH]
        left_lines = n - b0
        budget_left = max(0, max_images - len(keys))
        aim = max(1, round(budget_left * len(batch) / left_lines))
        lines = "\n".join(f"{b0 + j}. {s['text']}" for j, s in enumerate(batch))
        prompt = (
            f"You are planning images for a finance video about: {topic}\n"
            "Below are numbered narration lines. Choose ONE image for each line.\n"
            'Rules:\n- "key": 2 to 5 lowercase words naming the main visual idea (example: "man sleeping hotel bed").\n'
            "- If a line is about the same visual idea as an EARLIER line (including earlier batches, listed below), "
            'reuse that EXACT key and set "visual" to "".\n'
            '- Otherwise invent a new key and write "visual": one concrete sentence describing a photorealistic scene '
            "that matches the line (setting, action, objects). No text, logos or words inside the image.\n"
            "- Any person shown is a man aged 27 to 30 in a navy suit, unless the line is about a child (show a child), "
            "an old man (show an old man), a woman, or a group (show that instead).\n"
            "- Avoid using the same key for two lines in a row.\n"
            f"- Image budget: about {aim} NEW keys in this batch, {budget_left} left for the whole video. "
            "Reuse earlier keys wherever the idea truly matches.\n"
            f"Existing keys: {json.dumps(keys[-60:])}\n"
            'Return ONLY a JSON array like [{"i":12,"key":"...","visual":"..."}] with one object per line.\n'
            f"Lines:\n{lines}"
        )
        got = {}
        try:
            raw = ask(prompt, max_tokens=3500, temperature=0.5,
                      validate=lambda t: (lambda p: p is not None and len(p) >= 0.6 * len(batch))(_parse(t)))
            for d in _parse(raw):
                try:
                    got[int(d["i"])] = (_norm_key(d["key"]), str(d.get("visual", "")).strip())
                except Exception:
                    pass
        except Exception as e:
            print(f"[planner] batch {b0} failed ({e}); using fallback")
        prev = scenes[b0 - 1]["key"] if b0 else None
        for j, sc in enumerate(batch):
            idx = b0 + j
            key, vis = got.get(idx, (None, ""))
            if not key:                                   # fallback for a missing line
                if len(keys) < max_images and random.random() < aim / len(batch) + 0.3:
                    key, vis = f"scene {idx}", f"cinematic photorealistic scene illustrating: {sc['text']}"
                else:
                    key = prev or f"scene {idx}"
            if key not in visuals:
                if len(keys) >= max_images and keys:
                    key = _closest(key, keys)
                else:
                    visuals[key] = vis or f"cinematic photorealistic scene illustrating: {sc['text']}"
                    keys.append(key)
            sc["key"] = key
            prev = key
    print(f"[planner] {n} scenes, {len(keys)} unique images")
    return visuals

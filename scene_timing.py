"""Cuts the narration into 5-7 second scenes and plans one image per scene.
Scenes that repeat an earlier visual idea reuse that exact image (different zoom/transition)."""
import math
import random

from config import SCENE_MIN_SEC, SCENE_MAX_SEC

BATCH = 30


def build_scenes(sentences, durations, rng=None):
    rng = rng or random.Random()
    units = []
    for s, d in zip(sentences, durations):
        w = s.split()
        if d > 4.5 and len(w) > 1:
            n = min(math.ceil(d / 3.5), len(w))
            size = len(w) / n
            for k in range(n):
                part = w[round(k * size):round((k + 1) * size)]
                if part:
                    units.append((" ".join(part), d * len(part) / len(w)))
        else:
            units.append((s, d))
    scenes, acc, acc_d, t = [], [], 0.0, 0.0
    target = rng.uniform(5.2, 6.5)

    def close():
        nonlocal acc, acc_d, t, target
        scenes.append({"text": " ".join(acc), "start": t, "dur": acc_d})
        t += acc_d
        acc, acc_d, target = [], 0.0, rng.uniform(5.2, 6.5)

    for i, (text, d) in enumerate(units):
        if acc and acc_d + d > SCENE_MAX_SEC and acc_d >= SCENE_MIN_SEC:
            close()
        acc.append(text)
        acc_d += d
        nxt = units[i + 1][1] if i + 1 < len(units) else 99
        if acc_d >= SCENE_MIN_SEC and (acc_d >= target or acc_d + nxt > SCENE_MAX_SEC):
            close()
    if acc:
        if acc_d < SCENE_MIN_SEC and scenes and scenes[-1]["dur"] + acc_d <= 10.5:
            scenes[-1]["text"] += " " + " ".join(acc)
            scenes[-1]["dur"] += acc_d
        else:
            close()
    return scenes



"""Cached backgrounds drawn by code. Each returns (image, stickman_color)."""
import functools
import math
import random

import numpy as np
from PIL import Image

from draw import Ctx

GROUND = 0.80
DARK, LIGHT = (30, 33, 46), (245, 247, 252)


def _grad(W, H, top, bot, y1):
    y1 = int(y1)
    t = np.linspace(0, 1, max(1, y1))[:, None, None]
    sky = (np.array(top)[None, None, :] * (1 - t) + np.array(bot)[None, None, :] * t)
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:y1] = np.broadcast_to(sky, (y1, W, 3)).astype(np.uint8)
    return arr


def _ground(arr, y, col, col2=None):
    arr[int(y):] = col
    if col2:
        arr[int(y):int(y) + max(2, arr.shape[0] // 80)] = col2


def _make(name, W, H):
    gy = H * GROUND
    m = min(W, H)
    rnd = random.Random(name)
    col = DARK
    if name == "night":
        arr = _grad(W, H, (12, 16, 40), (40, 52, 100), gy)
        _ground(arr, gy, (26, 30, 52), (60, 70, 120))
        col = LIGHT
    elif name == "dusk":
        arr = _grad(W, H, (90, 70, 150), (255, 170, 110), gy)
        _ground(arr, gy, (70, 60, 90), (110, 90, 120))
    elif name == "room":
        arr = _grad(W, H, (236, 226, 208), (226, 212, 190), gy)
        _ground(arr, gy, (176, 124, 82), (140, 96, 62))
    elif name == "office":
        arr = _grad(W, H, (226, 232, 240), (206, 214, 226), gy)
        _ground(arr, gy, (150, 156, 168), (120, 126, 140))
    elif name == "money":
        arr = _grad(W, H, (22, 120, 80), (60, 170, 110), gy)
        _ground(arr, gy, (20, 90, 62), (40, 130, 90))
    elif name == "plain":
        arr = _grad(W, H, (240, 244, 252), (214, 226, 246), gy)
        _ground(arr, gy, (196, 208, 230), (170, 186, 214))
    elif name == "park":
        arr = _grad(W, H, (140, 205, 250), (215, 240, 255), gy)
        _ground(arr, gy, (110, 190, 100), (80, 160, 80))
    elif name == "city":
        arr = _grad(W, H, (150, 195, 240), (235, 235, 245), gy)
        _ground(arr, gy, (110, 114, 126), (80, 84, 96))
    else:  # day
        arr = _grad(W, H, (110, 190, 250), (205, 235, 255), gy)
        _ground(arr, gy, (118, 196, 108), (86, 164, 84))
    img = Image.fromarray(arr)
    c = Ctx(img)
    if name == "night":
        for _ in range(70):
            x, y, r = rnd.random() * W, rnd.random() * gy * 0.8, rnd.choice([1, 1, 2, 3]) * m / 700
            c.d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 240, 255))
        c.push(W * 0.85, H * 0.18, m * 0.12)
        c.circle(0, 0, 0.5, (250, 240, 200))
        c.pop()
    elif name == "day" or name == "park":
        c.push(W * 0.88, H * 0.16, m * 0.14)
        c.circle(0, 0, 0.4, (255, 215, 90))
        c.pop()
        for cx, cy, s in [(0.2, 0.15, 0.2), (0.55, 0.1, 0.16), (0.75, 0.28, 0.14)]:
            c.push(W * cx, H * cy, m * s)
            for x, y, r in [(-0.25, 0.05, 0.22), (0, -0.08, 0.28), (0.26, 0.05, 0.22)]:
                c.circle(x, y, r, (255, 255, 255))
            c.pop()
        if name == "park":
            for x in (0.06, 0.4, 0.93):
                c.push(W * x, gy, m * 0.3)
                c.rect(-0.04, -0.4, 0.04, 0, (140, 95, 55))
                c.circle(0, -0.55, 0.26, (60, 160, 80))
                c.pop()
    elif name == "dusk":
        c.push(W * 0.7, gy, m * 0.3)
        c.circle(0, 0, 0.5, (255, 214, 140))
        c.pop()
        for i in range(8):
            x = i / 7 * W
            c.poly([(x - W * 0.14, gy), (x, gy - H * (0.1 + 0.08 * rnd.random())), (x + W * 0.14, gy)], (60, 52, 100))
    elif name == "city":
        x = 0
        while x < W:
            w = m * (0.1 + 0.12 * rnd.random())
            h = H * (0.25 + 0.4 * rnd.random())
            shade = rnd.randint(120, 170)
            c.d.rectangle((x, gy - h, x + w, gy), fill=(shade, shade + 8, shade + 24))
            for wy in range(int(gy - h + w * 0.2), int(gy - w * 0.2), int(max(8, m * 0.05))):
                for wx in range(int(x + w * 0.15), int(x + w * 0.8), int(max(8, m * 0.05))):
                    c.d.rectangle((wx, wy, wx + m * 0.02, wy + m * 0.025), fill=(235, 235, 190) if rnd.random() < 0.4 else (100, 120, 150))
            x += w + m * 0.01
    elif name == "room":
        c.push(W * 0.12, H * 0.1, m * 0.4)
        c.rect(0, 0, 0.9, 0.7, (150, 205, 250), (130, 100, 70), 0.04)
        c.line([(0.45, 0), (0.45, 0.7)], 0.03, (130, 100, 70))
        c.line([(0, 0.35), (0.9, 0.35)], 0.03, (130, 100, 70))
        c.pop()
        c.push(W * 0.82, H * 0.16, m * 0.2)
        c.rect(0, 0, 0.7, 0.5, (250, 250, 250), (130, 100, 70), 0.04)
        c.line([(0.1, 0.38), (0.25, 0.2), (0.4, 0.3), (0.6, 0.08)], 0.04, (60, 170, 100))
        c.pop()
    elif name == "office":
        c.push(W * 0.1, H * 0.1, m * 0.55)
        c.rect(0, 0, 1.0, 0.62, (180, 214, 245), (120, 126, 140), 0.03)
        for i in range(1, 5):
            c.line([(0, i * 0.124), (1.0, i * 0.124)], 0.012, (150, 160, 180))
        c.pop()
        c.push(W * 0.88, gy, m * 0.3)
        c.rect(-0.12, -0.2, 0.12, 0, (180, 110, 70))
        for x, y in [(-0.12, -0.35), (0.0, -0.5), (0.12, -0.35)]:
            c.ellipse(x, y, 0.08, 0.2, (60, 160, 90))
        c.pop()
    elif name == "money":
        for i in range(40):
            c.text(rnd.random() * W, rnd.random() * gy, "$", m * (0.05 + 0.1 * rnd.random()), (50, 150, 100))
    return img, col


@functools.lru_cache(maxsize=12)
def get_bg(name, W, H):
    return _make(name, W, H)


BACKGROUNDS = ["day", "park", "dusk", "night", "room", "office", "city", "money", "plain"]

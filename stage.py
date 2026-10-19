"""Composes one scene. ONE big stickman by default, TWO (Poor vs Rich) only for comparison lines.
Shirt colors: blue = neutral, red = poor, green = rich."""
import math
import numpy as np
from PIL import Image

import props as P
import props_extra
import rig
import rig_extra
from auto_draw import register_auto
from backgrounds import get_bg, GROUND
from config import SUPERSAMPLE, TEXT_SCENE_USE_WHITE
from draw import Ctx, font
from stickers import draw_sticker


def back_out(x):
    c1 = 1.70158
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (c1 + 1) * x ** 3 + c1 * x ** 2


def layout(W, H):
    gy = H * GROUND
    if W >= H: # HORIZONTAL (LONG YOUTUBE VIDEOS)
        return dict(gy=gy, one=0.65 * H, two=0.55 * H, one_x=0.25 * W,
                    slots=[(0.75 * W, 0.55 * H, 0.45 * H), (0.90 * W, 0.35 * H, 0.30 * H), (0.55 * W, 0.30 * H, 0.26 * H)],
                    badge=0.075 * H)
    # VERTICAL (TIKTOK/SHORTS) - MASSIVE CHARACTERS
    return dict(gy=gy, one=0.75 * H, two=0.60 * H, one_x=0.30 * W,
                slots=[(0.75 * W, 0.45 * W, 0.65 * H), (0.76 * W, 0.30 * W, 0.42 * H), (0.55 * W, 0.26 * W, 0.24 * H)],
                badge=0.075 * W)


def _wrap_lines(text, size_px, max_w):
    f = font(int(size_px))
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        try:
            wpx = f.getbbox(cand)[2] - f.getbbox(cand)[0]
        except Exception:
            wpx = len(cand) * size_px * 0.55
        if wpx <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_text_frame(scene, W, H):
    S = SUPERSAMPLE
    WW, HH = W * S, H * S
    text = (scene.get("text_overlay") or scene.get("text") or "").strip()
    color_key = scene.get("text_color", "ink")
    bg_col = (250, 250, 252) if TEXT_SCENE_USE_WHITE else (18, 20, 30)
    ink = (30, 33, 46) if TEXT_SCENE_USE_WHITE else (250, 250, 252)
    accent = (224, 72, 72) if color_key == "accent" else ink
    size_px = HH * 0.10
    while True:
        lines = _wrap_lines(text, size_px, WW * 0.82)
        if len(lines) <= 8 or size_px < HH * 0.04:
            break
        size_px *= 0.9
    line_h = size_px * 1.22

    def frame(t):
        img = Image.new("RGB", (WW, HH), bg_col)
        c = Ctx(img)
        c.rect(WW * 0.06, HH * 0.5 - line_h * len(lines) * 0.6, WW * 0.062, HH * 0.5 + line_h * len(lines) * 0.6, accent)
        c.push(WW * 0.5, HH * 0.5 - line_h * (len(lines) - 1) * 0.5, 1.0)
        for i, ln in enumerate(lines):
            c.text(0, i * line_h, ln, size_px, accent if i == 0 and color_key == "accent" else ink)
        c.pop()
        return np.asarray(img.resize((W, H), Image.BOX))
    return frame


def make_scene_frame(scene, W, H):
    if scene.get("mode") == "text":
        return make_text_frame(scene, W, H)
    S = SUPERSAMPLE
    WW, HH = W * S, H * S
    L = layout(WW, HH)
    bg_name = scene.get("bg", "day")
    emo = scene.get("emotion", "neutral")
    action = scene.get("action", "idle")
    dual = bool(scene.get("dual"))
    who = scene.get("who")
    prop_names = []
    for p in (scene.get("props", []) or []):
        prop_names.append(p if p in P.PROPS else register_auto(p))
    prop_names = prop_names[:1] if dual else prop_names[:3]
    slots = list(L["slots"])
    if dual:
        slots[0] = (0.5 * WW, 0.22 * min(WW, HH), 0.30 * HH)
    badge = scene.get("item_label", "")
    badge_pop = bool(scene.get("item_start"))
    dual_labels = scene.get("dual_labels") or ("POOR", "RICH")
    stickers = scene.get("stickers", []) or []
    action2 = scene.get("dual_action_2", "celebrate")
    emo2 = scene.get("dual_emotion_2", "happy")

    def frame(t):
        base, col = get_bg(bg_name, WW, HH)
        img = base.copy()
        c = Ctx(img)
        for i in sorted(range(len(prop_names)), key=lambda j: -j):
            fn, kind = P.PROPS[prop_names[i]]
            x, size, fy = slots[i]
            k = back_out((t - 0.12 - 0.22 * i) / 0.45)
            if k <= 0.01:
                continue
            size *= k
            cy = L["gy"] - size / 2 + size * 0.02 if kind == "g" else fy + 0.012 * HH * math.sin(t * 1.8 + i)
            c.push(x, cy, size)
            fn(c, max(0.0, t - 0.12 - 0.22 * i))
            c.pop()

        if dual:
            # RENDER SIDE-BY-SIDE (POOR left, RICH right)
            figs = [(0.28, action, emo, dual_labels[0], (224, 72, 72), rig.SHIRT_RED),
                    (0.72, action2, emo2, dual_labels[1], (52, 168, 92), rig.SHIRT_GREEN)]
            size = L["two"]
        else:
            figs = [(L["one_x"] / WW, action, emo, None, None, rig.SHIRTS.get(who, rig.SHIRT_WHITE))]
            size = L["one"]

        for xf, act, em, label, lc, shirt in figs:
            p = rig.pose_at(act, t)
            if act in ("walk", "run", "sneak", "pace", "march"):
                p["dx"] += 0.15 * math.sin(t * 0.7)
            
            # soft ground shadow
            try:
                px = base.getpixel((int(WW * xf), min(HH - 1, int(L["gy"]) + 6)))
                shade = tuple(int(v * 0.80) for v in px[:3])
            except Exception:
                shade = (200, 205, 216)
            c.push(WW * xf, L["gy"], size)
            c.ellipse(0, 0, 0.32, 0.035, shade)
            c.pop()
            
            # DRAW CHARACTER
            c.push(WW * xf, L["gy"], size)
            rig.draw_stick(c, p, em, t, col, shirt=shirt)
            c.pop()
            
            # DRAW "POOR" / "RICH" ABOVE HEAD
            if label:
                # Position exactly above the huge head
                c.push(WW * xf, L["gy"] - size * 1.05, size * 0.14)
                c.text(0, 0.02, label, 1.0, lc)
                c.pop()

        if badge:
            land = WW >= HH
            if dual:
                spots = [(0.18, 0.12), (0.82, 0.12)] if land else [(0.5, 0.19)]
            elif land:
                spots = [(0.82, 0.13), (0.50, 0.92), (0.80, 0.92), (0.20, 0.92)]
            else:
                spots = [(0.50, 0.92), (0.28, 0.92), (0.72, 0.92), (0.50, 0.19)]
            bx, by = spots[sum(map(ord, badge)) % len(spots)]
            k = back_out(t / 0.5) if badge_pop else 1.0
            hw = max(1.2, 0.3 * len(badge) + 0.45)
            base_s = 0.15 * HH if land else 0.20 * WW
            sz = min(base_s, 0.8 * WW / (2 * hw)) * k
            c.push(WW * bx, HH * by, sz)
            c.rect(-hw, -0.7, hw, 0.7, (250, 196, 44), (38, 42, 56), 0.08, 0.3)
            c.text(0, 0.02, badge, 0.9, (38, 42, 56))
            c.pop()
        for st in stickers[:2]:
            draw_sticker(c, WW, HH, st.get("text", "").upper(), st.get("x", 0.5), st.get("y", 0.12),
                         st.get("size", 0.12), t, color=st.get("color", "gold"))
        return np.asarray(img.resize((W, H), Image.BOX))
    return frame

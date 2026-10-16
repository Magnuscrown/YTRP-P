"""Composes one scene. Always draws two stickmen side by side for the psychology channel."""
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

HAPPY = {"happy","excited","laughing","confident","proud","delighted","loved","inspired"}

def back_out(x):
    c1 = 1.70158
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (c1 + 1) * x ** 3 + c1 * x ** 2

def layout(W, H):
    gy = H * GROUND
    if W >= H:
        return dict(gy=gy, stick_h=0.40*H, stick_x=0.27*W,
                    slots=[(0.70*W, 0.50*H, 0.42*H), (0.90*W, 0.30*H, 0.30*H), (0.48*W, 0.28*H, 0.26*H)],
                    badge=0.075*H)
    return dict(gy=gy, stick_h=0.22*H, stick_x=0.25*W,
                slots=[(0.70*W, 0.50*W, 0.50*H), (0.50*W, 0.30*W, 0.28*H), (0.86*W, 0.28*W, 0.30*H)],
                badge=0.075*W)

def _wrap_lines(text, size_px, max_w):
    f = font(int(size_px))
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        try: wpx = f.getbbox(cand)[2] - f.getbbox(cand)[0]
        except Exception: wpx = len(cand) * size_px * 0.55
        if wpx <= max_w or not cur: cur = cand
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def make_text_frame(scene, W, H):
    S = SUPERSAMPLE
    WW, HH = W*S, H*S
    text = (scene.get("text_overlay") or scene.get("text") or "").strip()
    color_key = scene.get("text_color", "ink")
    bg_col = (250, 250, 252) if TEXT_SCENE_USE_WHITE else (18, 20, 30)
    ink = (30, 33, 46) if TEXT_SCENE_USE_WHITE else (250, 250, 252)
    accent = (224, 72, 72) if color_key == "accent" else ink
    size_px = HH * 0.10
    while True:
        lines = _wrap_lines(text, size_px, WW*0.82)
        if len(lines) <= 8 or size_px < HH*0.04: break
        size_px *= 0.9
    line_h = size_px * 1.22
    def frame(t):
        img = Image.new("RGB", (WW, HH), bg_col)
        c = Ctx(img)
        c.rect(WW*0.06, HH*0.5 - line_h*len(lines)*0.6, WW*0.062, HH*0.5 + line_h*len(lines)*0.6, accent)
        c.push(WW*0.5, HH*0.5 - line_h*(len(lines)-1)*0.5, 1.0)
        for i, ln in enumerate(lines):
            c.text(0, i*line_h, ln, size_px, accent if i == 0 and color_key == "accent" else ink)
        c.pop()
        return np.asarray(img.resize((W, H), Image.BOX))
    return frame

def make_scene_frame(scene, W, H):
    if scene.get("mode") == "text":
        return make_text_frame(scene, W, H)
    S = SUPERSAMPLE
    WW, HH = W*S, H*S
    L = layout(WW, HH)
    bg_name = scene.get("bg", "day")
    emo = scene.get("emotion", "neutral")
    action = scene.get("action", "idle")
    raw_props = scene.get("props", []) or []
    prop_names = []
    for p in raw_props:
        if p in P.PROPS: prop_names.append(p)
        else: prop_names.append(register_auto(p))
    prop_names = prop_names[:3]
    slots = list(L["slots"])
    if H > W:
        kinds = [P.PROPS[n][1] for n in prop_names]
        if len(kinds) > 1 and kinds[1] == "g": slots[1] = (0.47*WW, 0.30*WW, 0.28*HH)
        if len(kinds) > 1 and kinds[0] == "g" and kinds[1] == "g": slots[0] = (0.75*WW, 0.44*WW, 0.5*HH)
        if len(kinds) > 2 and kinds[2] == "g": prop_names = prop_names[:2]
    badge = scene.get("item_label", "")
    badge_pop = bool(scene.get("item_start"))
    walking = action in ("walk","run","sneak","pace","march","tiptoe","skip","spin")
    dual_labels = scene.get("dual_labels") or ("POOR", "RICH")
    stickers = scene.get("stickers", []) or []
    dual_action_2 = scene.get("dual_action_2", "celebrate")
    dual_emotion_2 = scene.get("dual_emotion_2", "happy")

    def frame(t):
        base, col = get_bg(bg_name, WW, HH)
        img = base.copy()
        c = Ctx(img)
        # Draw props
        for i in sorted(range(len(prop_names)), key=lambda j: -j):
            name = prop_names[i]
            fn, kind = P.PROPS[name]
            x, size, fy = slots[i]
            k = back_out((t - 0.12 - 0.22*i) / 0.45)
            if k <= 0.01: continue
            size *= k
            cy = L["gy"] - size/2 + size*0.02 if kind == "g" else fy + 0.012*HH*math.sin(t*1.8 + i)
            c.push(x, cy, size)
            fn(c, max(0.0, t - 0.12 - 0.22*i))
            c.pop()
        # Draw DUAL stickmen (Poor left, Rich right)
        for ax, xfrac, action_name, label, lbl_col in [
            (emo, 0.28, action, dual_labels[0], (224, 72, 72)),       # POOR = red
            (dual_emotion_2, 0.72, dual_action_2, dual_labels[1], (52, 168, 92)), # RICH = green
        ]:
            p = rig.pose_at(action_name, t)
            if action_name in ("walk","run","sneak","pace","march"): p["dx"] += 0.15*math.sin(t*0.7)
            c.push(WW*xfrac, L["gy"], L["stick_h"]*0.85)
            rig.draw_stick(c, p, ax, t, col)
            c.pop()
            c.push(WW*xfrac, L["gy"] + L["stick_h"]*0.92, L["stick_h"]*0.10)
            c.rect(-1.6, -0.6, 1.6, 0.6, lbl_col, (20, 20, 30), 0.06, 0.3)
            c.text(0, 0.02, label, 1.0, (250, 250, 250))
            c.pop()
        # Badge
        if badge:
            k = back_out(t / 0.5) if badge_pop else 1.0
            b = L["badge"] * k
            hw = max(1.2, 0.3*len(badge) + 0.45)
            c.push(WW*0.04 + b*hw, HH*0.04 + b*0.7, b)
            c.rect(-hw, -0.7, hw, 0.7, (250, 196, 44), (38, 42, 56), 0.08, 0.3)
            c.text(0, 0.02, badge, 0.9, (38, 42, 56))
            c.pop()
        # Stickers
        for st in stickers[:2]:
            txt = st.get("text", "").upper()
            col_key = st.get("color", "gold")
            xf = st.get("x", 0.5); yf = st.get("y", 0.22); sz = st.get("size", 0.12)
            draw_sticker(c, WW, HH, txt, xf, yf, sz, t, color=col_key)
        return np.asarray(img.resize((W, H), Image.BOX))
    return frame

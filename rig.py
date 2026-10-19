"""Stickman rig: forward-kinematics skeleton, ~20 actions, 10 emotions with faces and effects.
Big-head cartoon style with a colored shirt, hands and oval shoes."""
import math

from draw import Ctx

# --- THE BIG HEAD UPGRADE ---
TORSO, NECK, HR = 0.24, 0.03, 0.38
UA, LA, UL, LL = 0.16, 0.16, 0.20, 0.20
LW = 0.035  # Thicker, bolder lines

# shirt colors: blue = neutral/trust, red = POOR, green = RICH, white = default
SHIRT_BLUE = (52, 110, 225)
SHIRT_RED = (224, 72, 72)
SHIRT_GREEN = (52, 168, 92)
SHIRT_WHITE = (255, 255, 255)
SHIRTS = {"poor": SHIRT_RED, "rich": SHIRT_GREEN, None: SHIRT_WHITE}


def up(th):
    r = math.radians(th)
    return (math.sin(r), -math.cos(r))


def dn(th):
    r = math.radians(th)
    return (math.sin(r), math.cos(r))


def add(p, d, l):
    return (p[0] + d[0] * l, p[1] + d[1] * l)


BASE = dict(torso=0.0, head=0.0, au=8.0, al=14.0, bu=-8.0, bl=-14.0, lu=6.0, ll=2.0, ru=-6.0, rl=-2.0,
            jump=0.0, dx=0.0, lie=0.0, hold=None)


def S(t, f, a=1.0, ph=0.0):
    return a * math.sin(2 * math.pi * f * t + ph)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- actions
def a_idle(t):
    return dict(au=8 + S(t, .4, 4), al=14 + S(t, .4, 6), bu=-8 - S(t, .4, 4), bl=-14 - S(t, .4, 6),
                torso=S(t, .3, 1.5), head=S(t, .25, 3))


def _gait(t, f, amp, bend, arm, lean, hop, elbow):
    s, c = S(t, f), S(t, f, 1, math.pi / 2)
    lu, ru = amp * s, -amp * s
    return dict(lu=lu, ll=lu - bend * max(0, c), ru=ru, rl=ru - bend * max(0, -c),
                au=-arm * s, al=-arm * s + elbow, bu=arm * s, bl=arm * s + elbow,
                torso=lean, jump=hop * abs(S(t, f * 2)))


def a_walk(t):
    return _gait(t, 1.0, 28, 22, 26, 3, 0.012, 15)


def a_run(t):
    return _gait(t, 1.9, 48, 60, 50, 14, 0.05, 85)


def a_point(t):
    return dict(au=98 + S(t, .8, 4), al=98 + S(t, .8, 4), bu=-32, bl=30, torso=5 + S(t, .5, 1.5), head=4)


def a_wave(t):
    return dict(au=150, al=150 + S(t, 2.5, 28), head=S(t, .8, 4), torso=S(t, .8, 2))


def a_shrug(t):
    k = ease(t / 0.3)
    return dict(au=8 + 37 * k, al=14 + 120 * k, bu=-8 - 25 * k, bl=-14 - 100 * k,
                head=12 * k * (1 + .2 * S(t, 1.2)), torso=-2 * k, jump=0.01 * S(t, 1.5) ** 2)


def a_celebrate(t):
    h = abs(S(t, 1.5))
    return dict(au=160 + S(t, 3, 12), al=168 + S(t, 3, 16), bu=-160 - S(t, 3, 12, 1), bl=-168 - S(t, 3, 16, 1),
                lu=8, ru=-8, ll=-6, rl=6, jump=0.10 * h, torso=S(t, 1.5, 3), head=S(t, 1.5, 6))


def a_count_money(t):
    return dict(au=48, al=95 + S(t, 3, 18), bu=22, bl=92 + S(t, 3, 18, math.pi), head=14, torso=7, hold="money")


def a_think(t):
    return dict(au=25, al=160 + S(t, .6, 4), bu=-6, bl=-12, head=10 + S(t, .4, 3), torso=3)


def a_facepalm(t):
    return dict(au=30, al=170, head=20, torso=8 + S(t, .5, 1))


def a_sit(t):
    return dict(lu=88, ll=94, ru=84, rl=90, au=35, al=70, bu=20, bl=60, torso=2 + S(t, .3, 1), head=S(t, .3, 3))


def a_fall(t):
    p = ease(t / 0.8)
    return dict(torso=-88 * p, lu=4 + 84 * p, ll=2 + 88 * p, ru=-4 + 80 * p, rl=-2 + 86 * p,
                au=8 - 70 * p, al=14 - 80 * p, bu=-8 + 60 * p, bl=-14 + 70 * p, head=-6 * p, lie=p, dx=-0.12 * p)


def a_phone(t):
    return dict(au=42, al=148, bu=-8, bl=-14, head=16 + S(t, .4, 2), torso=5, hold="phone")


def a_slump(t):
    return dict(torso=14 + S(t, .3, 1.5), head=24, au=14, al=8, bu=-4, bl=-8, lu=8, ll=-6, ru=2, rl=-8)


def a_scared(t):
    k = ease(t / 0.25)
    tr = S(t, 9, 1.2)
    return dict(lu=22 * k, ll=-8 * k, ru=-10 * k, rl=-26 * k, au=55 + 10 * k, al=165, bu=38, bl=158,
                torso=-4 * k + tr, head=-6 * k, dx=-0.08 * k)


def a_angry(t):
    return dict(au=-18, al=62, bu=-40, bl=42, torso=S(t, 11, 1.8), head=-6, lu=S(t, 3, 12), ll=S(t, 3, 12) - 8)


def a_clap(t):
    m = S(t, 3.5, 22)
    return dict(au=48, al=96 + m, bu=36, bl=82 - m, head=S(t, .8, 3))


def a_jump(t):
    return dict(au=150, al=155, bu=-150, bl=-155, lu=10, ru=-10, jump=0.14 * abs(S(t, 1.2)))


def a_look(t):
    return dict(au=62, al=168, bu=-8, bl=-14, head=S(t, .6, 26), torso=S(t, .6, 3))


def a_sneak(t):
    s = S(t, 0.8)
    return dict(lu=30 + 10 * s, ll=-10, ru=-5, rl=-30, torso=18, head=-8, au=-20, al=-5, bu=30, bl=40)


ACTIONS = {
    "idle": a_idle, "walk": a_walk, "run": a_run, "point": a_point, "wave": a_wave, "shrug": a_shrug,
    "celebrate": a_celebrate, "count_money": a_count_money, "think": a_think, "facepalm": a_facepalm,
    "sit": a_sit, "fall": a_fall, "phone": a_phone, "slump": a_slump, "scared": a_scared,
    "angry": a_angry, "clap": a_clap, "jump": a_jump, "look": a_look, "sneak": a_sneak,
}


def pose_at(action, t):
    p = dict(BASE)
    idle = a_idle(t)
    p.update(idle)
    act = ACTIONS.get(action, a_idle)(t)
    k = ease(t / 0.25)           # blend in from idle so scene changes feel smooth
    for key, val in act.items():
        if isinstance(val, (int, float)) and isinstance(p.get(key), (int, float)) and key not in ("lie",):
            p[key] = p[key] + (val - p[key]) * k
        else:
            p[key] = val
    return p


# ---------------------------------------------------------------- faces
# THE NEW EMOTIONS FOR RICH AND POOR
EMO = {
    "neutral":   dict(eye="dot", brow="none", mouth="flat", extra=None),
    "happy":     dict(eye="arc", brow="none", mouth="smile", extra=None),
    "excited":   dict(eye="wide", brow="up", mouth="big", extra="sparkle"),
    "shocked":   dict(eye="wide", brow="up", mouth="o", extra="exclaim"),
    "worried":   dict(eye="dot", brow="worry", mouth="wavy", extra="sweat"),
    "sad":       dict(eye="dot", brow="worry", mouth="frown", extra="tear"),
    "angry":     dict(eye="dot", brow="angry", mouth="grit", extra="steam"),
    "confident": dict(eye="bored", brow="up1", mouth="smirk", extra=None),   # RICH
    "smug":      dict(eye="bored", brow="up1", mouth="smirk", extra=None),   # RICH
    "bored":     dict(eye="bored", brow="none", mouth="flat", extra=None),   # POOR
    "exhausted": dict(eye="tired", brow="worry", mouth="frown", extra="sweat"), # POOR
    "thinking":  dict(eye="dot", brow="up1", mouth="flat", extra="question"),
    "laughing":  dict(eye="arc", brow="up", mouth="big", extra=None),
}
BLUE = (80, 160, 235)


def face(c, hx, hy, r, emo, t, col, extras=True, fill=(255, 255, 255)):
    e = EMO.get(emo, EMO["neutral"])
    fx = hx + r * 0.10
    ey = hy - r * 0.05
    blink = (t % 3.5) < 0.12
    eyes = [fx - r * 0.42, fx + r * 0.42]
    
    for ex in eyes:
        if blink and e["eye"] not in ("arc", "bored", "tired"):
            c.line([(ex - r * .20, ey), (ex + r * .20, ey)], 0.02, col)
        elif e["eye"] == "wide":
            c.ellipse(ex, ey, r * 0.22, r * 0.28, fill, col, 0.025)
            c.circle(ex + r * 0.05, ey, r * 0.10, col)
        elif e["eye"] == "bored":
            c.arc(ex, ey, r * 0.20, 180, 360, 0.025, col)
            c.line([(ex - r * .22, ey), (ex + r * .22, ey)], 0.02, col)
            c.circle(ex, ey + r*0.05, r * 0.08, col)
        elif e["eye"] == "tired":
            c.arc(ex, ey - r*0.05, r * 0.20, 0, 180, 0.025, col)
            c.circle(ex, ey + r*0.05, r * 0.08, col)
            c.line([(ex - r * .15, ey - r*0.15), (ex + r * .15, ey - r*0.15)], 0.02, col)
        elif e["eye"] == "dot":
            c.circle(ex, ey, r * 0.14, col)
        else:
            c.arc(ex, ey + r * 0.06, r * 0.20, 200, 340, 0.025, col)

    b = e["brow"]
    if b != "none":
        for i, ex in enumerate(eyes):
            sgn = 1 if i == 0 else -1
            y0 = ey - r * 0.42
            if b == "up":
                p = [(ex - r * .22, y0 - r * .15), (ex + r * .22, y0 - r * .15)]
            elif b == "up1":
                p = [(ex - r * .22, y0 - (r * .18 if i else 0)), (ex + r * .22, y0 - (r * .18 if i else 0))]
            elif b == "worry":
                p = [(ex - sgn * r * .22, y0), (ex + sgn * r * .22, y0 - r * .20)]
            else:
                p = [(ex - sgn * r * .22, y0 - r * .15), (ex + sgn * r * .22, y0 + r * .08)]
            c.line(p, 0.03, col)

    m, my = e["mouth"], hy + r * 0.50
    if m == "smile":
        c.arc(fx, my - r * 0.25, r * 0.40, 25, 155, 0.025, col)
    elif m == "big":
        c.pie(fx, my - r * 0.22, r * 0.35, 0, 180, col)
    elif m == "o":
        c.circle(fx, my, r * 0.18, col)
    elif m == "frown":
        c.arc(fx, my + r * 0.25, r * 0.35, 205, 335, 0.025, col)
    elif m == "flat":
        c.line([(fx - r * .25, my), (fx + r * .25, my)], 0.025, col)
    elif m == "wavy":
        c.line([(fx - r * .35, my), (fx - r * .15, my - r * .10), (fx, my + r * .08), (fx + r * .15, my - r * .10), (fx + r * .35, my)], 0.025, col)
    elif m == "grit":
        c.rect(fx - r * .35, my - r * .15, fx + r * .35, my + r * .15, fill, col, 0.02)
        c.line([(fx, my - r * .15), (fx, my + r * .15)], 0.015, col)
    elif m == "smirk":
        c.line([(fx - r * .25, my), (fx + r * .15, my), (fx + r * .35, my - r * .18)], 0.025, col)
    
    x = e["extra"] if extras else None
    if x == "sweat":
        d = (t * 0.8) % 1
        c.ellipse(hx - r * 0.95, hy - r * 0.3 + d * r * 0.8, r * .1, r * .16, BLUE)
    elif x == "tear":
        d = (t * 0.7) % 1
        c.ellipse(eyes[1] + r * .05, ey + r * (0.2 + d * 1.0), r * .08, r * .13, BLUE)
    elif x == "exclaim":
        k = 1 + 0.15 * math.sin(t * 12)
        c.text(hx + r * 0.1, hy - r * 1.9, "!", r * 1.3 * k, (225, 60, 60))
    elif x == "question":
        c.text(hx + r * 0.1, hy - r * 1.9, "?", r * 1.3, (140, 90, 200))
    elif x == "steam":
        for i in (-1, 1):
            d = (t * 1.5 + (0.5 if i > 0 else 0)) % 1
            c.circle(hx + i * r * 0.7, hy - r * (1.2 + d * 0.7), r * (0.22 - 0.12 * d), (225, 70, 70))
    elif x == "sparkle":
        for i, (ox, oy) in enumerate([(-1.2, -1.1), (1.3, -0.9), (0.2, -1.6)]):
            k = 0.5 + 0.5 * math.sin(t * 6 + i * 2)
            sz = r * 0.3 * k
            sx, sy = hx + ox * r, hy + oy * r
            c.line([(sx - sz, sy), (sx + sz, sy)], 0.01, (250, 190, 40))
            c.line([(sx, sy - sz), (sx, sy + sz)], 0.01, (250, 190, 40))


# ---------------------------------------------------------------- body
def skeleton(p):
    o = (0.0, 0.0)
    sh = add(o, up(p["torso"]), TORSO * 0.9)
    neck = add(o, up(p["torso"]), TORSO)
    head = add(neck, up(p["torso"] + p["head"]), NECK + HR)
    ea = add(sh, dn(p["au"]), UA)
    ha = add(ea, dn(p["al"]), LA)
    eb = add(sh, dn(p["bu"]), UA)
    hb = add(eb, dn(p["bl"]), LA)
    ka = add(o, dn(p["lu"]), UL)
    fa = add(ka, dn(p["ll"]), LL)
    kb = add(o, dn(p["ru"]), UL)
    fb = add(kb, dn(p["rl"]), LL)
    return dict(sh=sh, neck=neck, head=head, ea=ea, ha=ha, eb=eb, hb=hb, ka=ka, fa=fa, kb=kb, fb=fb)


def draw_stick(c, p, emo, t, col, show_face=True, extras=True, shirt=SHIRT_WHITE):
    """c is pushed so (0,0) = ground contact point, 1 unit = stickman height."""
    k = skeleton(p)
    foot = max(k["fa"][1], k["fb"][1])
    hip_y = -((1 - p["lie"]) * foot + p["lie"] * 0.05) - p["jump"]
    c.push(p["dx"], hip_y, 1.0)
    dark = sum(col) > 450          
    fill = (30, 33, 46) if dark else (255, 255, 255)
    L = lambda *pts: c.line(list(pts), LW, col)

    def shoe(f):
        c.ellipse(f[0] + 0.05, f[1] - 0.035, 0.09, 0.045, fill, col, LW * 0.8)

    def hand(h):
        c.circle(h[0], h[1], 0.06, fill, col, LW * 0.7)

    def sleeve(sh, el):
        mid = (sh[0] + (el[0] - sh[0]) * 0.6, sh[1] + (el[1] - sh[1]) * 0.6)
        c.line([sh, mid], LW * 5.5, col)
        c.line([sh, mid], LW * 4.0, shirt)

    # back leg + back arm
    L((0, 0), k["kb"], k["fb"])
    shoe(k["fb"])
    L(k["sh"], k["eb"], k["hb"])
    sleeve(k["sh"], k["eb"])
    hand(k["hb"])
    # colored shirt
    th = math.radians(p["torso"])
    px, py = math.cos(th), math.sin(th)
    top, w0, w1 = k["neck"], 0.12, 0.10
    c.poly([(-px * w0, -py * w0), (px * w0, py * w0),
            (top[0] + px * w1, top[1] + py * w1), (top[0] - px * w1, top[1] - py * w1)],
           shirt, col, LW * 0.8)
    # front leg + front arm
    L((0, 0), k["ka"], k["fa"])
    shoe(k["fa"])
    L(k["sh"], k["ea"], k["ha"])
    sleeve(k["sh"], k["ea"])
    hand(k["ha"])
    hold = p.get("hold")
    if hold:
        x, y = k["ha"]
        if hold == "phone":
            c.rect(x - .05, y - .11, x + .05, y + .03, (50, 55, 70), None, 0.01, 0.015)
        elif hold == "money":
            for i in range(3):
                c.rect(x - .08 + i * .03, y - .08 - i * .015, x + .09 + i * .03, y + .0 - i * .015, (60, 170, 95), (30, 90, 50), 0.006)
    hxx, hyy = k["head"]
    c.circle(hxx, hyy, HR, fill, col, LW * 0.9)
    if show_face:
        face(c, hxx, hyy, HR, emo, t, col, extras, fill)
    c.pop()

# --- hook for extra actions + emotions ---
try:
    import rig_extra  # noqa
except Exception as _e:
    print(f"[rig] rig_extra not loaded: {_e}")

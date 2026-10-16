"""~80 props drawn by code. Each prop draws inside a unit box [-0.5,0.5]^2 (y down).
kind 'g' = stands on the ground, 'f' = floats."""
import math

INK = (38, 42, 56)
WHITE = (255, 255, 255)
GREEN = (52, 168, 92)
DGREEN = (30, 120, 70)
LGREEN = (140, 210, 130)
GOLD = (250, 196, 44)
DGOLD = (200, 140, 20)
RED = (224, 72, 72)
BLUE = (70, 130, 225)
LBLUE = (160, 205, 245)
GRAY = (150, 156, 170)
LGRAY = (212, 216, 224)
BROWN = (150, 95, 55)
PINK = (245, 150, 175)
PURPLE = (140, 90, 200)
ORANGE = (245, 140, 50)
CYAN = (90, 210, 230)
CREAM = (245, 225, 185)
W_ = 0.025

PROPS = {}


def reg(name, kind):
    def deco(fn):
        PROPS[name] = (fn, kind)
        return fn
    return deco


def prog(pts, p):
    """Points along a polyline up to fraction p."""
    if p >= 1:
        return list(pts)
    lens = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    goal, out = sum(lens) * p, [pts[0]]
    for i, L in enumerate(lens):
        if goal >= L:
            out.append(pts[i + 1])
            goal -= L
        else:
            f = goal / L if L else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            break
    return out


def grow(t, delay=0.0, dur=1.2):
    x = min(max((t - delay) / dur, 0), 1)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ money
@reg("money_stack", "g")
def _(c, t):
    for i in range(5):
        y = 0.5 - 0.16 * (i + 1)
        c.rect(-0.42, y, 0.42, y + 0.16, GREEN if i % 2 else LGREEN, INK, W_, 0.02)
    c.circle(0, -0.22, 0.08, GOLD, INK, 0.015)
    c.text(0, -0.22, "$", 0.12, INK)


@reg("coin", "f")
def _(c, t):
    k = abs(math.cos(t * 2.2)) * 0.9 + 0.1
    c.ellipse(0, 0, 0.42 * k, 0.42, GOLD, DGOLD, 0.04)
    if k > 0.4:
        c.ellipse(0, 0, 0.3 * k, 0.3, None, DGOLD, 0.02)
        c.text(0, 0, "$", 0.4 * k, DGOLD)


@reg("coins_pile", "g")
def _(c, t):
    for row in range(4):
        n = 4 - row
        for i in range(n):
            c.ellipse((i - (n - 1) / 2) * 0.24, 0.38 - row * 0.17, 0.13, 0.1, GOLD, DGOLD, 0.02)
    c.text(0, 0.0, "$", 0.16, DGOLD)


@reg("dollar_sign", "f")
def _(c, t):
    k = 1 + 0.06 * math.sin(t * 4)
    c.circle(0, 0, 0.42 * k, GREEN, DGREEN, 0.04)
    c.text(0, 0.02, "$", 0.62 * k, WHITE)


@reg("wallet", "g")
def _(c, t):
    c.rect(-0.3, -0.12, 0.2, 0.06, GREEN, INK, W_)
    c.rect(-0.45, -0.02, 0.45, 0.46, BROWN, INK, W_, 0.06)
    c.rect(-0.45, -0.02, 0.45, 0.14, (120, 72, 40), INK, W_, 0.05)
    c.circle(0.3, 0.2, 0.06, GOLD, INK, 0.015)


@reg("piggy_bank", "g")
def _(c, t):
    d = (t % 1.3) / 1.3
    c.circle(0, -0.46 + d * 0.3, 0.07, GOLD, DGOLD, 0.015)
    c.rect(-0.27, 0.3, -0.15, 0.5, PINK, INK, W_, 0.02)
    c.rect(0.12, 0.3, 0.24, 0.5, PINK, INK, W_, 0.02)
    c.ellipse(0, 0.08, 0.42, 0.3, PINK, INK, W_)
    c.poly([(0.1, -0.18), (0.22, -0.34), (0.3, -0.12)], PINK, INK, 0.02)
    c.ellipse(0.44, 0.08, 0.09, 0.12, PINK, INK, 0.02)
    c.circle(0.24, -0.04, 0.03, INK)
    c.line([(-0.1, -0.2), (0.1, -0.2)], 0.025, INK)
    c.line([(-0.42, 0.0), (-0.52, -0.06), (-0.46, -0.14)], 0.02, INK)


@reg("credit_card", "f")
def _(c, t):
    c.push(0, 0.02 * math.sin(t * 2), 1)
    c.rect(-0.46, -0.3, 0.46, 0.3, BLUE, INK, W_, 0.05)
    c.rect(-0.46, -0.18, 0.46, -0.05, INK)
    c.rect(-0.36, 0.03, -0.14, 0.2, GOLD, DGOLD, 0.01, 0.02)
    for i in range(4):
        c.rect(-0.1 + i * 0.12, 0.12, -0.03 + i * 0.12, 0.2, LBLUE)
    c.pop()


@reg("cash_bag", "g")
def _(c, t):
    col = (210, 175, 115)
    c.poly([(-0.14, -0.1), (0.14, -0.1), (0.3, -0.34), (-0.3, -0.34)], col, INK, W_)
    c.ellipse(0, 0.18, 0.38, 0.32, col, INK, W_)
    c.rect(-0.16, -0.14, 0.16, -0.07, RED, INK, 0.015)
    c.text(0, 0.18, "$", 0.34, DGREEN)


@reg("gold_bar", "g")
def _(c, t):
    def bar(x, y):
        c.poly([(x - 0.2, y - 0.07), (x + 0.2, y - 0.07), (x + 0.28, y + 0.11), (x - 0.28, y + 0.11)], GOLD, INK, 0.02)
        c.poly([(x - 0.2, y - 0.07), (x + 0.2, y - 0.07), (x + 0.16, y - 0.02), (x - 0.16, y - 0.02)], (255, 225, 120))
    for x in (-0.3, 0, 0.3):
        bar(x, 0.38)
    for x in (-0.15, 0.15):
        bar(x, 0.17)
    bar(0, -0.04)


@reg("safe", "g")
def _(c, t):
    c.rect(-0.4, -0.4, 0.4, 0.46, GRAY, INK, W_, 0.04)
    c.rect(-0.32, -0.32, 0.32, 0.38, LGRAY, INK, 0.02, 0.03)
    c.circle(0, 0, 0.14, GRAY, INK, 0.025)
    a = math.radians(t * 80)
    c.line([(0, 0), (math.cos(a) * 0.12, math.sin(a) * 0.12)], 0.025, INK)
    c.rect(-0.34, 0.46, -0.24, 0.5, INK)
    c.rect(0.24, 0.46, 0.34, 0.5, INK)


@reg("calculator", "f")
def _(c, t):
    c.rect(-0.32, -0.46, 0.32, 0.46, (60, 64, 80), INK, W_, 0.05)
    c.rect(-0.25, -0.38, 0.25, -0.18, LGREEN, INK, 0.015)
    c.text(0.2, -0.28, "$1,000", 0.07, INK, "rm")
    for r in range(4):
        for k in range(3):
            c.rect(-0.24 + k * 0.17, -0.1 + r * 0.14, -0.1 + k * 0.17, 0.02 + r * 0.14, GOLD if k == 2 else LGRAY, None, 0.01, 0.02)


@reg("bank", "g")
def _(c, t):
    c.poly([(-0.5, -0.12), (0, -0.46), (0.5, -0.12)], LGRAY, INK, W_)
    c.text(0, -0.2, "$", 0.16, DGREEN)
    for i in range(4):
        c.rect(-0.4 + i * 0.27, -0.1, -0.3 + i * 0.27, 0.36, WHITE, INK, 0.02)
    c.rect(-0.5, 0.36, 0.5, 0.43, LGRAY, INK, 0.02)
    c.rect(-0.45, 0.43, 0.45, 0.5, GRAY, INK, 0.02)


@reg("chart_up", "f")
def _(c, t):
    c.rect(-0.5, -0.4, 0.5, 0.4, WHITE, INK, W_, 0.04)
    c.line([(-0.4, -0.3), (-0.4, 0.3), (0.42, 0.3)], 0.025, GRAY)
    pts = [(-0.36, 0.22), (-0.2, 0.08), (-0.08, 0.15), (0.1, -0.05), (0.2, 0.02), (0.38, -0.26)]
    q = prog(pts, grow(t, 0.1, 1.6))
    if len(q) > 1:
        c.line(q, 0.05, GREEN)
        x, y = q[-1]
        c.poly([(x + 0.07, y - 0.07), (x - 0.04, y - 0.06), (x + 0.06, y + 0.04)], GREEN)


@reg("chart_down", "f")
def _(c, t):
    c.rect(-0.5, -0.4, 0.5, 0.4, WHITE, INK, W_, 0.04)
    c.line([(-0.4, -0.3), (-0.4, 0.3), (0.42, 0.3)], 0.025, GRAY)
    pts = [(-0.36, -0.24), (-0.2, -0.1), (-0.08, -0.16), (0.1, 0.05), (0.2, -0.02), (0.38, 0.24)]
    q = prog(pts, grow(t, 0.1, 1.6))
    if len(q) > 1:
        c.line(q, 0.05, RED)
        x, y = q[-1]
        c.poly([(x + 0.07, y + 0.07), (x - 0.04, y + 0.06), (x + 0.06, y - 0.04)], RED)


@reg("bar_chart", "f")
def _(c, t):
    c.rect(-0.5, -0.4, 0.5, 0.4, WHITE, INK, W_, 0.04)
    c.line([(-0.4, 0.3), (0.42, 0.3)], 0.025, GRAY)
    for i, h in enumerate([0.2, 0.35, 0.28, 0.5, 0.62]):
        hh = h * grow(t, i * 0.15, 0.7)
        c.rect(-0.38 + i * 0.16, 0.3 - hh, -0.26 + i * 0.16, 0.3, [BLUE, GREEN, GOLD, ORANGE, RED][i], INK, 0.012)


@reg("pie_chart", "f")
def _(c, t):
    a = 0
    for frac, col in [(0.4, BLUE), (0.25, GREEN), (0.2, GOLD), (0.15, RED)]:
        end = a + 360 * frac * grow(t, 0, 0.9)
        c.pie(0, 0, 0.42, a - 90, end - 90, col, INK, 0.02)
        a += 360 * frac


@reg("candles", "f")
def _(c, t):
    c.rect(-0.5, -0.4, 0.5, 0.4, (30, 34, 46), INK, W_, 0.04)
    data = [(0.15, 0.05, 0.2, 0, 1), (0.05, -0.08, 0.1, -0.14, 1), (-0.05, 0.08, -0.1, 0.14, 0), (0.1, -0.1, 0.14, -0.16, 1),
            (-0.12, 0.0, -0.16, 0.05, 0), (-0.02, -0.2, 0.02, -0.26, 1), (-0.18, -0.05, -0.24, 0.02, 0)]
    for i, (o, cl, hi, lo, up_) in enumerate(data):
        x = -0.36 + i * 0.12
        col = LGREEN if up_ else RED
        k = grow(t, i * 0.1, 0.4)
        c.line([(x, o * 2 - 0.1), (x, cl * 2 + 0.1)], 0.015, col)
        c.rect(x - 0.035, min(o, cl) * 2 - 0.06 * k, x + 0.035, max(o, cl) * 2 + 0.06 * k, col)


@reg("trophy", "g")
def _(c, t):
    c.arc(-0.27, -0.18, 0.13, 90, 270, 0.04, DGOLD)
    c.arc(0.27, -0.18, 0.13, -90, 90, 0.04, DGOLD)
    c.poly([(-0.28, -0.42), (0.28, -0.42), (0.22, -0.02), (0.08, 0.1), (-0.08, 0.1), (-0.22, -0.02)], GOLD, INK, W_)
    c.rect(-0.05, 0.1, 0.05, 0.3, GOLD, INK, 0.02)
    c.rect(-0.22, 0.3, 0.22, 0.46, DGOLD, INK, 0.02)
    c.text(0, -0.2, "1", 0.22, DGOLD)


@reg("diamond", "f")
def _(c, t):
    pts = [(-0.22, -0.3), (0.22, -0.3), (0.42, -0.06), (0, 0.42), (-0.42, -0.06)]
    c.poly(pts, CYAN, INK, W_)
    c.line([(-0.42, -0.06), (0.42, -0.06)], 0.015, INK)
    c.line([(-0.22, -0.3), (-0.1, -0.06), (0, 0.42), (0.1, -0.06), (0.22, -0.3)], 0.012, (40, 130, 160))
    k = 0.5 + 0.5 * math.sin(t * 5)
    c.line([(-0.3 - 0.1 * k, -0.35), (-0.3 + 0.1 * k, -0.35)], 0.015, WHITE)
    c.line([(-0.3, -0.35 - 0.1 * k), (-0.3, -0.35 + 0.1 * k)], 0.015, WHITE)


@reg("bills_rain", "f")
def _(c, t):
    for i in range(9):
        x = -0.42 + i * 0.105
        y = ((t * 0.5 + i * 0.37) % 1.1) - 0.55
        s = 0.04 * math.sin(t * 3 + i)
        c.poly([(x - 0.07 + s, y - 0.04), (x + 0.07 + s, y - 0.04), (x + 0.07 - s, y + 0.04), (x - 0.07 - s, y + 0.04)], GREEN, DGREEN, 0.012)


# ------------------------------------------------------------------ places
@reg("house", "g")
def _(c, t):
    c.rect(0.18, -0.4, 0.3, -0.18, RED, INK, 0.02)
    c.rect(-0.38, -0.08, 0.38, 0.5, CREAM, INK, W_)
    c.poly([(-0.5, -0.06), (0, -0.46), (0.5, -0.06)], RED, INK, W_)
    c.rect(-0.07, 0.2, 0.1, 0.5, BROWN, INK, 0.02)
    c.rect(-0.3, 0.04, -0.14, 0.2, LBLUE, INK, 0.02)
    c.rect(0.14, 0.04, 0.3, 0.2, LBLUE, INK, 0.02)


@reg("hotel", "g")
def _(c, t):
    c.rect(-0.34, -0.38, 0.34, 0.5, (232, 200, 160), INK, W_)
    c.rect(-0.38, -0.5, 0.38, -0.36, RED, INK, 0.02, 0.02)
    c.text(0, -0.43, "HOTEL", 0.11, WHITE)
    for r in range(5):
        for k in range(3):
            lit = math.sin(t * 0.7 + r * 2 + k * 3) > -0.2
            c.rect(-0.26 + k * 0.19, -0.28 + r * 0.12, -0.14 + k * 0.19, -0.2 + r * 0.12, (255, 230, 120) if lit else LBLUE, INK, 0.01)
    c.rect(-0.1, 0.28, 0.1, 0.5, BROWN, INK, 0.015)
    c.rect(-0.16, 0.22, 0.16, 0.28, RED, INK, 0.012)


@reg("skyscraper", "g")
def _(c, t):
    c.rect(-0.38, -0.12, -0.14, 0.5, (140, 156, 184), INK, 0.02)
    c.rect(-0.2, -0.5, 0.26, 0.5, (100, 120, 156), INK, W_)
    c.line([(0.03, -0.5), (0.03, -0.58)], 0.02, INK)
    for r in range(9):
        for k in range(3):
            lit = math.sin(t * 0.5 + r * 1.7 + k * 2.3) > -0.3
            c.rect(-0.14 + k * 0.13, -0.42 + r * 0.1, -0.06 + k * 0.13, -0.35 + r * 0.1, (255, 230, 120) if lit else (70, 84, 112))
    c.rect(0.26, 0.0, 0.46, 0.5, (130, 146, 174), INK, 0.02)


@reg("car", "g")
def _(c, t):
    c.push(0, 0.16, 1)
    c.poly([(-0.5, 0.2), (-0.5, 0.02), (-0.3, -0.02), (-0.18, -0.2), (0.2, -0.2), (0.36, -0.02), (0.5, 0.02), (0.5, 0.2)], BLUE, INK, W_)
    c.poly([(-0.16, -0.04), (-0.09, -0.16), (0.0, -0.16), (0.0, -0.04)], LBLUE, INK, 0.015)
    c.poly([(0.05, -0.04), (0.05, -0.16), (0.17, -0.16), (0.28, -0.04)], LBLUE, INK, 0.015)
    for x in (-0.28, 0.28):
        c.circle(x, 0.2, 0.12, INK)
        c.circle(x, 0.2, 0.05, LGRAY)
        a = t * 8
        c.line([(x + math.cos(a) * 0.05, 0.2 + math.sin(a) * 0.05), (x - math.cos(a) * 0.05, 0.2 - math.sin(a) * 0.05)], 0.015, GRAY)
    c.rect(0.46, 0.02, 0.5, 0.08, GOLD)
    c.pop()


@reg("sports_car", "g")
def _(c, t):
    c.push(0, 0.2, 1)
    c.poly([(-0.52, 0.16), (-0.5, 0.0), (-0.2, -0.04), (-0.05, -0.17), (0.18, -0.17), (0.3, -0.03), (0.52, 0.02), (0.52, 0.16)], RED, INK, W_)
    c.poly([(-0.02, -0.05), (0.04, -0.14), (0.16, -0.14), (0.24, -0.05)], LBLUE, INK, 0.015)
    for x in (-0.3, 0.3):
        c.circle(x, 0.16, 0.11, INK)
        c.circle(x, 0.16, 0.045, GOLD)
    c.pop()
    c.line([(-0.5, 0.3), (-0.58, 0.3)], 0.02, GRAY)


@reg("plane", "f")
def _(c, t):
    c.push(0.05 * math.sin(t * 1.5), 0.03 * math.sin(t * 2), 1)
    c.poly([(-0.3, -0.04), (-0.5, -0.3), (-0.38, -0.3), (-0.14, -0.04)], LGRAY, INK, 0.02)
    c.ellipse(0, 0, 0.46, 0.1, WHITE, INK, W_)
    c.poly([(-0.02, 0.02), (-0.24, 0.3), (-0.1, 0.3), (0.14, 0.02)], LGRAY, INK, 0.02)
    for i in range(5):
        c.circle(-0.2 + i * 0.1, -0.02, 0.025, LBLUE)
    c.pop()


@reg("boat", "g")
def _(c, t):
    c.line([(0, -0.46), (0, 0.1)], 0.03, INK)
    c.poly([(0.03, -0.44), (0.4, 0.06), (0.03, 0.06)], WHITE, INK, 0.02)
    c.poly([(-0.03, -0.36), (-0.3, 0.06), (-0.03, 0.06)], LBLUE, INK, 0.02)
    c.poly([(-0.46, 0.1), (0.46, 0.1), (0.3, 0.3), (-0.3, 0.3)], RED, INK, W_)
    pts = [(-0.5 + i * 0.05, 0.38 + 0.04 * math.sin(i * 0.9 + t * 3)) for i in range(21)]
    c.poly(pts + [(0.5, 0.5), (-0.5, 0.5)], (80, 150, 230))


@reg("world", "f")
def _(c, t):
    c.circle(0, 0, 0.44, BLUE, INK, 0.035)
    sh = 0.08 * math.sin(t * 0.8)
    for x, y, rx, ry in [(-0.15 + sh, -0.12, 0.17, 0.13), (0.18 - sh, 0.06, 0.13, 0.2), (-0.04 + sh, 0.28, 0.1, 0.07), (0.1, -0.28, 0.1, 0.05)]:
        c.ellipse(x, y, rx, ry, LGREEN)
    c.arc(0, 0, 0.44, 200, 250, 0.03, WHITE)


@reg("factory", "g")
def _(c, t):
    for x in (0.14, 0.3):
        c.rect(x - 0.05, -0.32, x + 0.05, 0.0, GRAY, INK, 0.02)
        for i in range(3):
            d = (t * 0.5 + i / 3.0) % 1
            c.circle(x + 0.03 * d, -0.36 - d * 0.14, 0.04 + 0.05 * d, LGRAY)
    c.rect(-0.46, -0.04, 0.46, 0.5, (190, 120, 90), INK, W_)
    for i in range(3):
        c.poly([(-0.46 + i * 0.2, -0.04), (-0.46 + i * 0.2, -0.2), (-0.26 + i * 0.2, -0.04)], (190, 120, 90), INK, 0.02)
    for i in range(4):
        c.rect(-0.38 + i * 0.2, 0.1, -0.26 + i * 0.2, 0.22, (255, 220, 120), INK, 0.012)
    c.rect(-0.08, 0.3, 0.08, 0.5, INK)


@reg("store", "g")
def _(c, t):
    c.rect(-0.42, -0.14, 0.42, 0.5, CREAM, INK, W_)
    for i in range(6):
        c.rect(-0.42 + i * 0.14, -0.2, -0.28 + i * 0.14, -0.02, RED if i % 2 == 0 else WHITE, INK, 0.012)
    c.rect(-0.3, -0.46, 0.3, -0.24, BLUE, INK, 0.02, 0.02)
    c.text(0, -0.35, "SHOP", 0.14, WHITE)
    c.rect(-0.34, 0.08, 0.0, 0.32, LBLUE, INK, 0.02)
    c.rect(0.1, 0.12, 0.3, 0.5, BROWN, INK, 0.02)


@reg("tree", "g")
def _(c, t):
    c.rect(-0.07, 0.05, 0.07, 0.5, BROWN, INK, 0.02)
    s = 0.01 * math.sin(t * 1.5)
    for x, y, r in [(0, -0.12, 0.32), (-0.2 + s, 0.0, 0.22), (0.2 - s, 0.0, 0.22)]:
        c.circle(x, y, r, GREEN, DGREEN, 0.02)


@reg("sun", "f")
def _(c, t):
    for i in range(12):
        a = math.radians(i * 30 + t * 20)
        c.line([(math.cos(a) * 0.3, math.sin(a) * 0.3), (math.cos(a) * 0.46, math.sin(a) * 0.46)], 0.04, GOLD)
    c.circle(0, 0, 0.24, GOLD, DGOLD, 0.03)


@reg("moon", "f")
def _(c, t):
    c.circle(0, 0, 0.38, (250, 240, 200), (220, 205, 150), 0.03)
    for x, y, r in [(-0.12, -0.1, 0.07), (0.14, 0.08, 0.09), (-0.05, 0.2, 0.05)]:
        c.circle(x, y, r, (230, 218, 170))


@reg("cloud", "f")
def _(c, t):
    s = 0.03 * math.sin(t)
    for x, y, r in [(-0.2 + s, 0.05, 0.2), (0.0, -0.08, 0.26), (0.22 + s, 0.05, 0.2)]:
        c.circle(x, y, r, WHITE, LGRAY, 0.02)
    c.rect(-0.2, 0.0, 0.22, 0.25, WHITE)


@reg("mountain", "g")
def _(c, t):
    c.poly([(-0.5, 0.5), (-0.1, -0.35), (0.3, 0.5)], (120, 130, 150), INK, W_)
    c.poly([(0.0, 0.5), (0.3, -0.1), (0.52, 0.5)], (140, 150, 170), INK, W_)
    c.poly([(-0.1, -0.35), (-0.2, -0.17), (-0.13, -0.2), (-0.1, -0.12), (-0.04, -0.2), (0.0, -0.17)], WHITE)
    c.line([(-0.1, -0.35), (-0.1, -0.5)], 0.02, INK)
    c.poly([(-0.1, -0.5), (0.06, -0.45 + 0.01 * math.sin(t * 5)), (-0.1, -0.4)], RED)


# ------------------------------------------------------------------ work / tech
@reg("laptop", "g")
def _(c, t):
    c.push(0, 0.16, 1)
    c.rect(-0.36, -0.3, 0.36, 0.2, (60, 66, 84), INK, W_, 0.03)
    c.rect(-0.3, -0.25, 0.3, 0.15, LBLUE)
    c.line(prog([(-0.24, 0.08), (-0.1, -0.02), (0.02, 0.04), (0.14, -0.12), (0.24, -0.2)], grow(t, 0, 1.5)), 0.03, GREEN)
    c.poly([(-0.46, 0.24), (0.46, 0.24), (0.52, 0.34), (-0.52, 0.34)], GRAY, INK, 0.02)
    c.pop()


@reg("phone", "f")
def _(c, t):
    c.rect(-0.2, -0.42, 0.2, 0.42, INK, INK, W_, 0.06)
    c.rect(-0.17, -0.35, 0.17, 0.34, LBLUE)
    for i in range(3):
        for k in range(2):
            c.rect(-0.12 + k * 0.13, -0.28 + i * 0.12, -0.03 + k * 0.13, -0.2 + i * 0.12, [RED, GREEN, GOLD, BLUE, PURPLE, ORANGE][i * 2 + k], None, 0.01, 0.015)
    if (t * 2) % 2 < 1:
        c.circle(0.17, -0.38, 0.06, RED)


@reg("desk", "g")
def _(c, t):
    c.rect(-0.5, -0.05, 0.5, 0.05, BROWN, INK, W_)
    c.rect(-0.44, 0.05, -0.36, 0.5, BROWN, INK, 0.02)
    c.rect(0.36, 0.05, 0.44, 0.5, BROWN, INK, 0.02)
    c.rect(0.0, 0.05, 0.34, 0.3, (130, 80, 45), INK, 0.02)
    c.rect(-0.3, -0.2, -0.05, -0.05, WHITE, INK, 0.015)
    c.rect(0.12, -0.17, 0.3, -0.05, LBLUE, INK, 0.015)


@reg("book", "f")
def _(c, t):
    c.rect(-0.28, -0.4, 0.28, 0.4, BLUE, INK, W_, 0.03)
    c.rect(-0.28, -0.4, -0.2, 0.4, (45, 85, 170), INK, 0.015)
    c.rect(-0.1, -0.24, 0.2, -0.16, GOLD)
    c.rect(-0.1, -0.1, 0.14, -0.05, GOLD)


@reg("books_stack", "g")
def _(c, t):
    for i, (col, w) in enumerate([(RED, 0.46), (GREEN, 0.4), (BLUE, 0.44), (GOLD, 0.34)]):
        y = 0.5 - 0.15 * (i + 1)
        c.rect(-w + 0.04 * (i % 2), y, w + 0.04 * (i % 2), y + 0.15, col, INK, 0.02, 0.01)
        c.line([(-w + 0.1 + 0.04 * (i % 2), y + 0.075), (-w + 0.3 + 0.04 * (i % 2), y + 0.075)], 0.02, WHITE)


@reg("briefcase", "g")
def _(c, t):
    c.push(0, 0.1, 1)
    c.line([(-0.12, -0.1), (-0.12, -0.24), (0.12, -0.24), (0.12, -0.1)], 0.04, INK)
    c.rect(-0.44, -0.1, 0.44, 0.4, BROWN, INK, W_, 0.05)
    c.line([(-0.44, 0.1), (0.44, 0.1)], 0.02, INK)
    c.rect(-0.05, 0.05, 0.05, 0.16, GOLD, INK, 0.01)
    c.pop()


@reg("clock", "f")
def _(c, t):
    c.circle(0, 0, 0.42, WHITE, INK, 0.04)
    for i in range(12):
        a = math.radians(i * 30)
        c.line([(math.sin(a) * 0.34, -math.cos(a) * 0.34), (math.sin(a) * 0.4, -math.cos(a) * 0.4)], 0.02, INK)
    m, h = math.radians(t * 90), math.radians(t * 7.5)
    c.line([(0, 0), (math.sin(m) * 0.32, -math.cos(m) * 0.32)], 0.025, INK)
    c.line([(0, 0), (math.sin(h) * 0.2, -math.cos(h) * 0.2)], 0.04, RED)
    c.circle(0, 0, 0.03, INK)


@reg("alarm_clock", "f")
def _(c, t):
    sh = 0.012 * math.sin(t * 40)
    c.push(sh, 0, 1)
    c.circle(-0.22, -0.34, 0.11, GOLD, INK, 0.02)
    c.circle(0.22, -0.34, 0.11, GOLD, INK, 0.02)
    c.line([(-0.28, 0.36), (-0.36, 0.46)], 0.04, INK)
    c.line([(0.28, 0.36), (0.36, 0.46)], 0.04, INK)
    c.circle(0, 0.03, 0.38, RED, INK, 0.03)
    c.circle(0, 0.03, 0.29, WHITE)
    c.line([(0, 0.03), (0, -0.2)], 0.025, INK)
    c.line([(0, 0.03), (0.13, 0.1)], 0.03, INK)
    c.pop()


@reg("calendar", "f")
def _(c, t):
    c.rect(-0.4, -0.42, 0.4, 0.42, WHITE, INK, W_, 0.04)
    c.rect(-0.4, -0.42, 0.4, -0.22, RED, INK, 0.02, 0.03)
    k = int(t * 2.5)
    for r in range(4):
        for q in range(5):
            x, y = -0.3 + q * 0.15, -0.12 + r * 0.14
            c.rect(x - 0.05, y - 0.05, x + 0.05, y + 0.05, LGRAY)
            if r * 5 + q < k:
                c.line([(x - 0.05, y - 0.05), (x + 0.05, y + 0.05)], 0.02, RED)
                c.line([(x - 0.05, y + 0.05), (x + 0.05, y - 0.05)], 0.02, RED)


@reg("lightbulb", "f")
def _(c, t):
    k = 0.5 + 0.5 * math.sin(t * 4)
    for i in range(7):
        a = math.radians(-90 + (i - 3) * 28)
        c.line([(math.cos(a) * 0.36, -0.12 + math.sin(a) * 0.36), (math.cos(a) * (0.42 + 0.06 * k), -0.12 + math.sin(a) * (0.42 + 0.06 * k))], 0.03, GOLD)
    c.circle(0, -0.12, 0.27, (255, 236, 130), INK, 0.03)
    c.poly([(-0.12, 0.08), (0.12, 0.08), (0.1, 0.18), (-0.1, 0.18)], (255, 236, 130), INK, 0.02)
    c.rect(-0.12, 0.18, 0.12, 0.34, GRAY, INK, 0.02)
    c.line([(-0.06, -0.1), (0, -0.2), (0.06, -0.1)], 0.02, DGOLD)


@reg("gear", "f")
def _(c, t):
    pts = []
    for i in range(16):
        a = math.radians(i * 22.5 + t * 40)
        r = 0.44 if i % 2 == 0 else 0.34
        pts.append((math.cos(a) * r, math.sin(a) * r))
    c.poly(pts, GRAY, INK, 0.025)
    c.circle(0, 0, 0.14, WHITE, INK, 0.025)


@reg("rocket", "f")
def _(c, t):
    c.push(0, 0.03 * math.sin(t * 3), 1)
    f = 0.1 * math.sin(t * 25)
    c.poly([(-0.08, 0.3), (0.08, 0.3), (0, 0.5 + f)], ORANGE)
    c.poly([(-0.04, 0.3), (0.04, 0.3), (0, 0.42 + f)], GOLD)
    c.poly([(-0.13, 0.0), (-0.3, 0.24), (-0.13, 0.22)], RED, INK, 0.02)
    c.poly([(0.13, 0.0), (0.3, 0.24), (0.13, 0.22)], RED, INK, 0.02)
    c.poly([(0, -0.46), (0.15, -0.22), (0.15, 0.3), (-0.15, 0.3), (-0.15, -0.22)], WHITE, INK, W_)
    c.poly([(0, -0.46), (0.15, -0.22), (-0.15, -0.22)], RED, INK, 0.02)
    c.circle(0, -0.06, 0.07, LBLUE, INK, 0.02)
    c.pop()


@reg("key", "f")
def _(c, t):
    c.circle(-0.22, 0, 0.18, None, GOLD, 0.07)
    c.line([(-0.04, 0), (0.42, 0)], 0.07, GOLD)
    c.line([(0.3, 0), (0.3, 0.14)], 0.06, GOLD)
    c.line([(0.4, 0), (0.4, 0.1)], 0.06, GOLD)


@reg("lock", "f")
def _(c, t):
    c.arc(0, -0.05, 0.19, 180, 360, 0.07, GRAY)
    c.line([(-0.19, -0.05), (-0.19, 0.02)], 0.07, GRAY)
    c.line([(0.19, -0.05), (0.19, 0.02)], 0.07, GRAY)
    c.rect(-0.3, 0.0, 0.3, 0.42, GOLD, INK, W_, 0.05)
    c.circle(0, 0.16, 0.05, INK)
    c.rect(-0.015, 0.16, 0.015, 0.3, INK)


@reg("megaphone", "f")
def _(c, t):
    c.poly([(-0.3, -0.12), (0.0, -0.12), (0.34, -0.36), (0.34, 0.36), (0.0, 0.12), (-0.3, 0.12)], RED, INK, W_)
    c.rect(-0.12, 0.1, -0.02, 0.34, INK)
    for i in range(3):
        k = (t * 1.5 + i / 3.0) % 1
        c.arc(0.34, 0, 0.1 + k * 0.16, -50, 50, 0.025, INK)


@reg("magnifier", "f")
def _(c, t):
    c.line([(0.14, 0.14), (0.42, 0.42)], 0.09, BROWN)
    c.circle(-0.08, -0.08, 0.3, (215, 238, 252), INK, 0.05)
    c.arc(-0.08, -0.08, 0.2, 200, 260, 0.03, WHITE)


@reg("target", "f")
def _(c, t):
    for r, col in [(0.44, RED), (0.34, WHITE), (0.24, RED), (0.14, WHITE), (0.06, RED)]:
        c.circle(0, 0, r, col, INK, 0.012)
    k = grow(t, 0.2, 0.35)
    c.line([(0.0 + 0.4 * (1 - k), -0.0 - 0.4 * (1 - k)), (0.42 + 0.4 * (1 - k), -0.42 - 0.4 * (1 - k))], 0.03, INK)


@reg("checkmark", "f")
def _(c, t):
    c.circle(0, 0, 0.42, GREEN, DGREEN, 0.04)
    c.line(prog([(-0.2, 0.0), (-0.05, 0.16), (0.22, -0.16)], grow(t, 0.1, 0.5)), 0.1, WHITE)


@reg("cross_mark", "f")
def _(c, t):
    c.circle(0, 0, 0.42, RED, (150, 40, 40), 0.04)
    k = grow(t, 0.1, 0.4)
    c.line(prog([(-0.18, -0.18), (0.18, 0.18)], k), 0.1, WHITE)
    c.line(prog([(0.18, -0.18), (-0.18, 0.18)], grow(t, 0.3, 0.4)), 0.1, WHITE)


@reg("question", "f")
def _(c, t):
    c.circle(0, 0, 0.42, PURPLE, (90, 50, 150), 0.04)
    c.text(0, 0.02, "?", 0.7, WHITE)


@reg("warning", "f")
def _(c, t):
    k = 1 + 0.05 * math.sin(t * 8)
    c.push(0, 0, k)
    c.poly([(0, -0.44), (0.46, 0.38), (-0.46, 0.38)], GOLD, INK, 0.04)
    c.text(0, 0.1, "!", 0.5, INK)
    c.pop()


@reg("heart", "f")
def _(c, t):
    k = 1 + 0.08 * math.sin(t * 6)
    c.push(0, 0, k)
    c.circle(-0.15, -0.1, 0.2, RED)
    c.circle(0.15, -0.1, 0.2, RED)
    c.poly([(-0.34, -0.02), (0.34, -0.02), (0, 0.4)], RED)
    c.pop()


@reg("fire", "f")
def _(c, t):
    j = 0.03 * math.sin(t * 12)
    c.poly([(j, -0.46), (0.2, -0.1), (0.3, 0.12), (0.14, 0.42), (-0.14, 0.42), (-0.3, 0.12), (-0.2, -0.1)], ORANGE, (200, 80, 30), 0.02)
    c.poly([(-j, -0.14), (0.13, 0.08), (0.16, 0.3), (-0.16, 0.3), (-0.13, 0.08)], GOLD)


@reg("arrow_up", "f")
def _(c, t):
    y = 0.04 * math.sin(t * 4)
    c.poly([(0, -0.44 + y), (0.36, 0.0 + y), (0.14, 0.0 + y), (0.14, 0.42 + y), (-0.14, 0.42 + y), (-0.14, 0.0 + y), (-0.36, 0.0 + y)], GREEN, DGREEN, 0.03)


@reg("arrow_down", "f")
def _(c, t):
    y = -0.04 * math.sin(t * 4)
    c.poly([(0, 0.44 + y), (0.36, 0.0 + y), (0.14, 0.0 + y), (0.14, -0.42 + y), (-0.14, -0.42 + y), (-0.14, 0.0 + y), (-0.36, 0.0 + y)], RED, (150, 40, 40), 0.03)


# ------------------------------------------------------------------ life
@reg("bed", "g")
def _(c, t):
    c.rect(-0.5, -0.32, -0.43, 0.5, BROWN, INK, 0.02)
    c.rect(-0.5, 0.12, 0.5, 0.28, BROWN, INK, 0.02)
    c.rect(0.44, 0.28, 0.5, 0.5, BROWN, INK, 0.02)
    c.rect(-0.45, -0.04, 0.47, 0.14, WHITE, INK, 0.02, 0.03)
    c.rect(-0.4, -0.16, -0.17, -0.02, LBLUE, INK, 0.02, 0.04)
    c.rect(-0.12, -0.1, 0.47, 0.14, BLUE, INK, 0.02, 0.03)
    for i in range(3):
        d = (t * 0.6 + i / 3.0) % 1
        c.text(-0.2 + d * 0.3, -0.25 - d * 0.22, "z", 0.12 + 0.05 * i, PURPLE)


@reg("coffee", "f")
def _(c, t):
    for i in range(3):
        d = (t * 0.8 + i / 3.0) % 1
        c.line([(-0.1 + i * 0.1 + 0.03 * math.sin(d * 8), -0.2 - d * 0.22), (-0.1 + i * 0.1, -0.3 - d * 0.22)], 0.02, GRAY)
    c.poly([(-0.26, -0.1), (0.26, -0.1), (0.2, 0.36), (-0.2, 0.36)], WHITE, INK, W_)
    c.arc(0.27, 0.1, 0.12, -90, 90, 0.04, INK)
    c.rect(-0.26, -0.1, 0.26, -0.04, BROWN)


@reg("burger", "f")
def _(c, t):
    c.pie(0, -0.02, 0.4, 180, 360, ORANGE, INK, 0.02)
    c.rect(-0.4, -0.04, 0.4, 0.04, LGREEN, INK, 0.015)
    c.rect(-0.4, 0.04, 0.4, 0.16, BROWN, INK, 0.015, 0.03)
    c.poly([(-0.38, 0.16), (0.38, 0.16), (0.0, 0.26)], GOLD)
    c.rect(-0.4, 0.2, 0.4, 0.34, ORANGE, INK, 0.015, 0.05)


@reg("shopping_cart", "g")
def _(c, t):
    c.push(0, 0.1, 1)
    c.line([(-0.5, -0.3), (-0.36, -0.3), (-0.26, 0.18), (0.38, 0.18)], 0.04, INK)
    c.poly([(-0.33, -0.18), (0.46, -0.18), (0.38, 0.1), (-0.27, 0.1)], LGRAY, INK, 0.03)
    for x in (-0.1, 0.1, 0.28):
        c.line([(x, -0.18), (x - 0.02, 0.1)], 0.015, INK)
    c.circle(-0.18, 0.3, 0.07, INK)
    c.circle(0.3, 0.3, 0.07, INK)
    c.pop()


@reg("shopping_bag", "f")
def _(c, t):
    c.arc(0, -0.18, 0.14, 180, 360, 0.035, INK)
    c.poly([(-0.34, -0.18), (0.34, -0.18), (0.4, 0.42), (-0.4, 0.42)], RED, INK, W_)
    c.text(0, 0.1, "%", 0.3, WHITE)


@reg("gift", "g")
def _(c, t):
    c.push(0, 0.12, 1)
    c.rect(-0.38, -0.12, 0.38, 0.38, BLUE, INK, W_)
    c.rect(-0.42, -0.24, 0.42, -0.08, LBLUE, INK, 0.02)
    c.rect(-0.05, -0.24, 0.05, 0.38, GOLD)
    c.circle(-0.1, -0.32, 0.1, None, GOLD, 0.045)
    c.circle(0.1, -0.32, 0.1, None, GOLD, 0.045)
    c.pop()


@reg("price_tag", "f")
def _(c, t):
    c.poly([(-0.42, 0.0), (-0.2, -0.3), (0.4, -0.3), (0.4, 0.3), (-0.2, 0.3)], RED, INK, W_)
    c.circle(-0.2, 0.0, 0.05, WHITE, INK, 0.015)
    c.text(0.12, 0.0, "SALE", 0.16, WHITE)


@reg("ladder", "g")
def _(c, t):
    c.line([(-0.2, -0.5), (-0.2, 0.5)], 0.05, BROWN)
    c.line([(0.2, -0.5), (0.2, 0.5)], 0.05, BROWN)
    for i in range(7):
        c.line([(-0.2, -0.4 + i * 0.14), (0.2, -0.4 + i * 0.14)], 0.04, BROWN)


@reg("flag", "g")
def _(c, t):
    c.line([(-0.2, -0.5), (-0.2, 0.5)], 0.04, INK)
    pts = [(-0.18 + i * 0.07, -0.46 + 0.02 * math.sin(i * 1.2 + t * 6)) for i in range(7)]
    pts2 = [(x, y + 0.3) for x, y in reversed(pts)]
    c.poly(pts + pts2, RED, INK, 0.015)


@reg("medal", "f")
def _(c, t):
    c.poly([(-0.2, -0.46), (-0.02, -0.46), (0.1, -0.05), (-0.08, -0.05)], RED)
    c.poly([(0.2, -0.46), (0.02, -0.46), (-0.1, -0.05), (0.08, -0.05)], BLUE)
    c.circle(0, 0.15, 0.27, GOLD, DGOLD, 0.04)
    c.text(0, 0.15, "1", 0.3, DGOLD)


@reg("grad_cap", "f")
def _(c, t):
    c.poly([(-0.2, 0.0), (-0.2, 0.2), (0, 0.3), (0.2, 0.2), (0.2, 0.0)], (60, 66, 90), INK, 0.02)
    c.poly([(0, -0.28), (0.5, -0.06), (0, 0.16), (-0.5, -0.06)], (50, 56, 80), INK, 0.025)
    c.line([(0.4, -0.04), (0.4, 0.22)], 0.02, GOLD)
    c.circle(0.4, 0.25, 0.04, GOLD)


@reg("hourglass", "f")
def _(c, t):
    f = (t * 0.25) % 1
    c.poly([(-0.26, -0.1 - 0.26 * (1 - f) * 0 - 0.3 + 0.3 * f), (0.26, -0.3 + 0.3 * f), (0.0, 0.0)], GOLD)
    c.poly([(-0.26 * f, 0.4), (0.26 * f, 0.4), (0, 0.4 - 0.3 * f)], GOLD)
    c.line([(0, 0), (0, 0.4)], 0.015, GOLD)
    c.poly([(-0.28, -0.4), (0.28, -0.4), (0.02, 0.0), (0.28, 0.4), (-0.28, 0.4), (-0.02, 0.0)], None, INK, 0.035)
    c.rect(-0.34, -0.46, 0.34, -0.4, BROWN, INK, 0.015)
    c.rect(-0.34, 0.4, 0.34, 0.46, BROWN, INK, 0.015)


@reg("scale", "f")
def _(c, t):
    tilt = 0.12 * math.sin(t * 1.6)
    c.line([(0, -0.4), (0, 0.4)], 0.04, INK)
    c.rect(-0.2, 0.4, 0.2, 0.46, INK)
    L, R = (-0.36, -0.3 - tilt), (0.36, -0.3 + tilt)
    c.line([L, R], 0.035, INK)
    for (x, y) in (L, R):
        c.line([(x, y), (x - 0.1, y + 0.3)], 0.01, INK)
        c.line([(x, y), (x + 0.1, y + 0.3)], 0.01, INK)
        c.poly([(x - 0.14, y + 0.3), (x + 0.14, y + 0.3), (x + 0.08, y + 0.36), (x - 0.08, y + 0.36)], GOLD, INK, 0.015)


@reg("plant_growth", "g")
def _(c, t):
    g = grow(t, 0.2, 2.2)
    c.poly([(-0.2, 0.2), (0.2, 0.2), (0.14, 0.5), (-0.14, 0.5)], (190, 100, 70), INK, 0.025)
    c.line([(0, 0.2), (0, 0.2 - 0.6 * g)], 0.04, DGREEN)
    for i, (s, y) in enumerate([(-1, 0.1), (1, -0.05), (-1, -0.2)]):
        if g > 0.3 + i * 0.2:
            k = min(1, (g - 0.3 - i * 0.2) * 4)
            c.ellipse(s * 0.14 * k, y, 0.14 * k, 0.07 * k, LGREEN, DGREEN, 0.015)


@reg("envelope", "f")
def _(c, t):
    c.rect(-0.44, -0.28, 0.44, 0.28, WHITE, INK, W_, 0.03)
    c.line([(-0.44, -0.28), (0, 0.06), (0.44, -0.28)], 0.025, INK)


@reg("contract", "f")
def _(c, t):
    c.rect(-0.3, -0.44, 0.3, 0.44, WHITE, INK, W_, 0.03)
    for i in range(5):
        c.line([(-0.2, -0.3 + i * 0.1), (0.2, -0.3 + i * 0.1)], 0.02, LGRAY)
    c.line(prog([(-0.2, 0.3), (-0.12, 0.2), (-0.05, 0.32), (0.03, 0.22), (0.16, 0.3)], grow(t, 0.3, 1.0)), 0.02, BLUE)
    c.circle(0.2, 0.28, 0.07, RED)


@reg("sofa", "g")
def _(c, t):
    c.rect(-0.46, -0.1, 0.46, 0.24, (110, 90, 170), INK, W_, 0.08)
    c.rect(-0.5, 0.04, -0.34, 0.36, (95, 75, 150), INK, 0.02, 0.05)
    c.rect(0.34, 0.04, 0.5, 0.36, (95, 75, 150), INK, 0.02, 0.05)
    c.rect(-0.36, 0.1, 0.36, 0.36, (125, 105, 190), INK, 0.02, 0.05)
    c.rect(-0.4, 0.36, -0.34, 0.5, INK)
    c.rect(0.34, 0.36, 0.4, 0.5, INK)


@reg("dumbbell", "g")
def _(c, t):
    c.push(0, 0.28, 1)
    c.line([(-0.3, 0), (0.3, 0)], 0.06, GRAY)
    for x in (-0.36, 0.36):
        c.rect(x - 0.05, -0.18, x + 0.05, 0.18, INK, None, 0.01, 0.02)
        c.rect(x - 0.05 - 0.07 * (1 if x < 0 else -1), -0.12, x + 0.0, 0.12, GRAY, INK, 0.015, 0.02)
    c.pop()


@reg("robot", "g")
def _(c, t):
    c.line([(0, -0.46), (0, -0.36)], 0.025, INK)
    c.circle(0, -0.48, 0.04, RED)
    c.rect(-0.2, -0.36, 0.2, -0.12, LGRAY, INK, 0.025, 0.04)
    c.circle(-0.08, -0.25, 0.04, CYAN)
    c.circle(0.08, -0.25, 0.04, CYAN)
    c.rect(-0.26, -0.1, 0.26, 0.28, GRAY, INK, W_, 0.04)
    c.rect(-0.1, 0.0, 0.1, 0.12, CYAN, INK, 0.015)
    c.line([(-0.26, -0.04), (-0.4, 0.14 + 0.05 * math.sin(t * 4))], 0.05, INK)
    c.line([(0.26, -0.04), (0.4, 0.14 - 0.05 * math.sin(t * 4))], 0.05, INK)
    c.rect(-0.18, 0.28, -0.06, 0.5, INK)
    c.rect(0.06, 0.28, 0.18, 0.5, INK)


@reg("brain", "f")
def _(c, t):
    k = 1 + 0.03 * math.sin(t * 3)
    c.push(0, 0, k)
    for x, y, r in [(-0.2, -0.1, 0.22), (0.18, -0.12, 0.22), (-0.1, 0.12, 0.2), (0.16, 0.1, 0.2), (0, -0.02, 0.22)]:
        c.circle(x, y, r, PINK, INK, 0.02)
    c.line([(0, -0.3), (0, 0.25)], 0.015, INK)
    c.arc(-0.12, 0.0, 0.1, 180, 360, 0.015, INK)
    c.arc(0.14, 0.0, 0.1, 0, 180, 0.015, INK)
    c.pop()


@reg("watch", "f")
def _(c, t):
    c.rect(-0.1, -0.5, 0.1, -0.2, BROWN, INK, 0.02)
    c.rect(-0.1, 0.2, 0.1, 0.5, BROWN, INK, 0.02)
    c.circle(0, 0, 0.28, GOLD, DGOLD, 0.04)
    c.circle(0, 0, 0.21, WHITE)
    a = math.radians(t * 90)
    c.line([(0, 0), (math.sin(a) * 0.17, -math.cos(a) * 0.17)], 0.02, INK)
    c.line([(0, 0), (0.0, -0.1)], 0.03, RED)


def catalog():
    return sorted(PROPS)

# --- hook for extra props ---
try:
    import props_extra  # noqa
except Exception as _e:
    print(f"[props] props_extra not loaded: {_e}")

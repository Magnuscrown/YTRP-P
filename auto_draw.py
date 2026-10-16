"""Backup drawing machine: when the AI asks for a prop we don't have, draw a generic card."""
import hashlib
from props import reg, PROPS, INK, WHITE, LGRAY

COLORS = [(70,130,225),(52,168,92),(224,72,72),(250,196,44),(140,90,200),
          (90,210,230),(245,140,50),(245,150,175)]

AUTO_PREFIX = "auto__"

def _h(name):
    return hashlib.md5(name.encode("utf-8")).hexdigest()

def _color(name):
    return COLORS[int(_h(name)[:2], 16) % len(COLORS)]

def _shape(name):
    return int(_h(name)[2:4], 16) % 6

def register_auto(name):
    """Register a fallback prop drawing for `name`. Returns the prop key."""
    key = AUTO_PREFIX + name[:32].replace(" ", "_").replace("-", "_")
    if key in PROPS:
        return key
    col = _color(name); shp = _shape(name)
    def draw(c, t):
        c.rect(-0.42, -0.42, 0.42, 0.42, WHITE, INK, 0.025, 0.05)
        if shp == 0:   c.circle(0, -0.1, 0.22, col, INK, 0.02)
        elif shp == 1: c.poly([(0,-0.32),(0.3,0.06),(-0.3,0.06)], col, INK, 0.02)
        elif shp == 2: c.rect(-0.24, -0.3, 0.24, 0.06, col, INK, 0.02, 0.05)
        elif shp == 3: c.poly([(0,-0.3),(0.3,-0.1),(0.2,0.15),(-0.2,0.15),(-0.3,-0.1)], col, INK, 0.02)
        elif shp == 4:
            c.circle(0,-0.1,0.24, None, col, 0.05); c.circle(0,-0.1,0.1, col)
        else:
            for i in range(3):
                c.rect(-0.28, -0.3 + i*0.18, 0.28, -0.18 + i*0.18,
                       col if i % 2 == 0 else LGRAY, INK, 0.015, 0.02)
        label = name.split()[0][:7].upper()
        c.text(0, 0.30, label, 0.11, INK)
    PROPS[key] = (draw, "f")
    return key

def is_auto(key):
    return key.startswith(AUTO_PREFIX)

"""Word sticker overlay. Called from stage.py per-scene when scene['stickers'] is set."""
import math
from draw import Ctx

PALETTE = {
    "gold":   ((250,196,44),(90,60,10)),
    "red":    ((224,72,72),(90,20,20)),
    "green":  ((52,168,92),(15,70,35)),
    "blue":   ((70,130,225),(20,50,120)),
    "purple": ((140,90,200),(60,25,110)),
    "white":  ((250,250,252),(30,33,46)),
}

def draw_sticker(c, W, H, text, x_frac, y_frac, size_frac, t, color="gold", pop=True):
    """text: any string.  x_frac/y_frac in [0,1] of frame.  size_frac of min(W,H)."""
    key = PALETTE.get(color, PALETTE["gold"])
    bg, ink = key
    k = 1.0 + (0.05*math.sin(t*8) if pop else 0.0)
    s = min(W, H) * size_frac * k
    x, y = W * x_frac, H * y_frac
    c.push(x, y, s)
    # ribbon
    c.rect(-1.9, -0.7, 1.9, 0.7, bg, ink, 0.10, 0.35)
    c.text(0, 0.02, text.upper()[:14], 1.0, ink)
    c.pop()

def default_stickers_for(text, emo):
    """Heuristic: if narration says a punchy word, return (word, color) to show."""
    t = text.lower()
    rules = [
        (r"\bfree\b",              "FREE",       "green"),
        (r"\bunlimited\b",         "UNLIMITED",  "blue"),
        (r"\bguaranteed\b",        "GUARANTEED", "red"),
        (r"\bmillionaire|million\b","MILLION",   "gold"),
        (r"\bbillionaire|billion\b","BILLION",   "gold"),
        (r"\bzero\b",              "ZERO",       "white"),
        (r"\b100%\b|\b100 percent\b","100%",     "purple"),
        (r"\bnever\b",             "NEVER",      "red"),
        (r"\balways\b",            "ALWAYS",     "green"),
        (r"\bwarning|danger\b",    "WARNING",    "red"),
        (r"\bsecret\b",            "SECRET",     "purple"),
        (r"\bmistake\b",           "MISTAKE",    "red"),
        (r"\bquit\b|\bstop\b",     "STOP",       "red"),
        (r"\bstart\b|\bstart today\b","START",   "green"),
        (r"\bnow\b",               "NOW",        "gold"),
        (r"\bbroke\b",             "BROKE",      "red"),
        (r"\brich\b",              "RICH",       "gold"),
    ]
    for pat, word, col in rules:
        import re
        if re.search(pat, t):
            return word, col
    return None

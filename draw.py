"""Tiny vector-style drawing layer on top of PIL with a translate/scale stack."""
import functools
from PIL import ImageDraw, ImageFont

FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


@functools.lru_cache(maxsize=256)
def font(px):
    px = max(6, int(px))
    for p in FONTS:
        try:
            return ImageFont.truetype(p, px)
        except Exception:
            continue
    return ImageFont.load_default()


class Ctx:
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.tx, self.ty, self.s = 0.0, 0.0, 1.0
        self._st = []

    def push(self, x, y, s=1.0):
        self._st.append((self.tx, self.ty, self.s))
        self.tx += x * self.s
        self.ty += y * self.s
        self.s *= s

    def pop(self):
        self.tx, self.ty, self.s = self._st.pop()

    def P(self, x, y):
        return (self.tx + x * self.s, self.ty + y * self.s)

    def _w(self, w):
        return max(1, int(round(w * self.s)))

    def line(self, pts, w, col, cap=True):
        pp = [self.P(*p) for p in pts]
        ww = self._w(w)
        self.d.line(pp, fill=col, width=ww, joint="curve")
        if cap and ww > 2:
            r = ww / 2.0
            for x, y in (pp[0], pp[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=col)

    def ellipse(self, x, y, rx, ry, fill=None, line=None, w=0.02):
        cx, cy = self.P(x, y)
        a, b = rx * self.s, ry * self.s
        kw = {"fill": fill}
        if line:
            kw.update(outline=line, width=self._w(w))
        self.d.ellipse((cx - a, cy - b, cx + a, cy + b), **kw)

    def circle(self, x, y, r, fill=None, line=None, w=0.02):
        self.ellipse(x, y, r, r, fill, line, w)

    def rect(self, x0, y0, x1, y1, fill=None, line=None, w=0.02, r=0.0):
        a, b = self.P(x0, y0), self.P(x1, y1)
        box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
        kw = {"fill": fill}
        if line:
            kw.update(outline=line, width=self._w(w))
        rad = min(r * self.s, (box[2] - box[0]) / 2 - 0.5, (box[3] - box[1]) / 2 - 0.5)
        if rad > 1:
            self.d.rounded_rectangle(box, radius=rad, **kw)
        else:
            self.d.rectangle(box, **kw)

    def poly(self, pts, fill=None, line=None, w=0.02):
        pp = [self.P(*p) for p in pts]
        if fill:
            self.d.polygon(pp, fill=fill)
        if line:
            self.d.line(pp + [pp[0]], fill=line, width=self._w(w), joint="curve")

    def arc(self, x, y, r, a0, a1, w, col):
        cx, cy = self.P(x, y)
        rr = r * self.s
        self.d.arc((cx - rr, cy - rr, cx + rr, cy + rr), a0, a1, fill=col, width=self._w(w))

    def pie(self, x, y, r, a0, a1, fill, line=None, w=0.02):
        cx, cy = self.P(x, y)
        rr = r * self.s
        kw = {"fill": fill}
        if line:
            kw.update(outline=line, width=self._w(w))
        self.d.pieslice((cx - rr, cy - rr, cx + rr, cy + rr), a0, a1, **kw)

    def text(self, x, y, s, size, col, anchor="mm"):
        self.d.text(self.P(x, y), s, font=font(size * self.s), fill=col, anchor=anchor)

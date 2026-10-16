"""Extra props: social stickers, more money, more objects. Imported by props.py."""
import math
from props import (reg, PROPS, INK, WHITE, GREEN, DGREEN, LGREEN, GOLD, DGOLD, RED, BLUE, LBLUE,
                   GRAY, LGRAY, BROWN, PINK, PURPLE, ORANGE, CYAN, CREAM, W_)

# ---------- YouTube / social stickers ----------
@reg("btn_subscribe", "f")
def _(c, t):
    p = 1 + 0.04*math.sin(t*5)
    c.push(0, 0, p)
    c.rect(-0.48, -0.16, 0.48, 0.16, RED, INK, 0.02, 0.08)
    c.text(0, 0.0, "SUBSCRIBE", 0.22, WHITE)
    c.pop()
@reg("btn_like", "f")
def _(c, t):
    p = 1 + 0.05*math.sin(t*6)
    c.push(0, 0, p)
    c.rect(-0.3, -0.2, 0.3, 0.2, LBLUE, INK, 0.02, 0.06)
    c.poly([(-0.2,0.0),(-0.2,0.2),(-0.02,0.2),(-0.02,0.0)], LBLUE)
    c.rect(-0.06, -0.14, 0.06, 0.2, LBLUE)
    c.rect(0.10, -0.14, 0.22, 0.2, LBLUE)
    c.text(0, 0.05, "+1", 0.32, BLUE)
    c.pop()
@reg("btn_bell", "f")
def _(c, t):
    sw = 0.06*math.sin(t*10)
    c.push(sw, 0, 1)
    c.poly([(-0.32,0.16),(0.32,0.16),(0.24,0.02),(0.24,-0.24),(-0.24,-0.24),(-0.24,0.02)], GOLD, DGOLD, 0.03)
    c.circle(0,-0.34,0.07, GOLD, DGOLD, 0.02)
    c.rect(-0.06,0.16,0.06,0.30, GOLD, DGOLD, 0.02)
    c.line([(-0.32,-0.12),(0.32,-0.12)], 0.03, DGOLD)
    c.pop()
@reg("btn_comment", "f")
def _(c, t):
    c.poly([(-0.4,-0.24),(0.4,-0.24),(0.4,0.14),(0.1,0.14),(0.02,0.30),(-0.05,0.14),(-0.4,0.14)], WHITE, INK, 0.03)
    for i in range(3):
        c.circle(-0.2+i*0.2, -0.04, 0.045, INK)
@reg("btn_share", "f")
def _(c, t):
    for x,y in [(-0.28,-0.28),(0.30,-0.02),(-0.28,0.24)]:
        c.circle(x, y, 0.11, GREEN, DGREEN, 0.02)
    c.line([(-0.20,-0.22),(0.24,-0.04)], 0.025, DGREEN)
    c.line([(-0.20,0.20),(0.24,0.02)], 0.025, DGREEN)
@reg("btn_play", "f")
def _(c, t):
    c.rect(-0.4,-0.24,0.4,0.24, RED, INK, 0.02, 0.06)
    c.poly([(-0.10,-0.13),(0.16,0.0),(-0.10,0.13)], WHITE)
@reg("btn_notify", "f")
def _(c, t):
    c.circle(0, 0, 0.42, RED, (150,30,30), 0.03)
    c.text(0, 0.0, "N", 0.55, WHITE)
@reg("youtube_logo", "f")
def _(c, t):
    c.rect(-0.48,-0.24,0.48,0.24, RED, INK, 0.02, 0.08)
    c.poly([(-0.1,-0.13),(0.18,0.0),(-0.1,0.13)], WHITE)
@reg("thumbs_up_big", "f")
def _(c, t):
    k = 1+0.06*math.sin(t*5)
    c.push(0,0,k)
    c.rect(-0.2,-0.1,0.2,0.3, LBLUE, BLUE, 0.02, 0.05)
    c.poly([(-0.3,-0.1),(-0.2,-0.1),(-0.2,0.3),(-0.3,0.3)], LBLUE, BLUE, 0.02)
    c.rect(-0.06,-0.4,0.06,-0.1, LBLUE, BLUE, 0.02)
    c.pop()

# ---------- more money / finance ----------
@reg("receipt", "f")
def _(c, t):
    c.poly([(-0.28,-0.4),(0.28,-0.4),(0.28,0.4),(-0.28,0.4)], WHITE, INK, W_)
    for i in range(6):
        c.line([(-0.18,-0.3+i*0.1),(0.18,-0.3+i*0.1)], 0.02, LGRAY)
    c.text(0, 0.34, "$48.20", 0.11, RED)
@reg("invoice", "f")
def _(c, t):
    c.rect(-0.28,-0.4,0.28,0.4, WHITE, INK, W_, 0.02)
    c.rect(-0.28,-0.4,0.28,-0.28, LGRAY, INK, 0.01)
    c.text(0, -0.34, "INVOICE", 0.1, INK)
    for i in range(4):
        c.line([(-0.2,-0.18+i*0.1), (0.2,-0.18+i*0.1)], 0.015, LGRAY)
@reg("tax_form", "f")
def _(c, t):
    c.rect(-0.3,-0.4,0.3,0.4, WHITE, INK, W_, 0.02)
    c.text(0, -0.32, "TAX", 0.16, RED)
    for i in range(5):
        c.rect(-0.22,-0.16+i*0.1, -0.06,-0.12+i*0.1, LGRAY, INK, 0.008)
        c.line([(0.0,-0.14+i*0.1),(0.22,-0.14+i*0.1)], 0.01, LGRAY)
@reg("mortgage", "f")
def _(c, t):
    c.rect(-0.34,-0.4,0.34,0.4, WHITE, INK, W_, 0.02)
    c.text(0, -0.3, "MORTGAGE", 0.09, INK)
    c.poly([(-0.2,-0.05),(0,-0.22),(0.2,-0.05)], CREAM, INK, 0.02)
    c.rect(-0.14,-0.05,0.14,0.15, CREAM, INK, 0.02)
    c.line([(-0.14,0.28),(0.14,0.28)], 0.02, INK)
@reg("ticker", "f")
def _(c, t):
    c.rect(-0.5,-0.14,0.5,0.14, INK, INK, W_)
    c.text(-0.4, 0, "AAPL", 0.13, LGREEN, anchor="lm")
    c.text(0.0, 0, "$192", 0.13, LGREEN, anchor="lm")
    c.text(0.36, 0, "▲", 0.13, LGREEN, anchor="lm")
@reg("ticker_down", "f")
def _(c, t):
    c.rect(-0.5,-0.14,0.5,0.14, INK, INK, W_)
    c.text(-0.4, 0, "MSFT", 0.13, RED, anchor="lm")
    c.text(0.0, 0, "$410", 0.13, RED, anchor="lm")
    c.text(0.36, 0, "▼", 0.13, RED, anchor="lm")
@reg("crypto_coin", "f")
def _(c, t):
    y = 0.05*math.sin(t*3)
    c.push(0, y, 1)
    c.circle(0, 0, 0.4, GOLD, DGOLD, 0.03)
    c.text(0, 0.0, "₿", 0.55, DGOLD)
    c.pop()
@reg("eth_coin", "f")
def _(c, t):
    c.poly([(0,-0.4),(0.3,-0.1),(0,0.4),(-0.3,-0.1)], (140,140,200), INK, 0.02)
    c.line([(0,-0.4),(0,0.4)], 0.015, INK)
@reg("retirement", "f")
def _(c, t):
    c.rect(-0.4,-0.34,0.4,0.34, WHITE, INK, W_, 0.04)
    c.text(0,-0.2, "401k", 0.22, DGREEN)
    c.circle(-0.16, 0.14, 0.08, GOLD, DGOLD, 0.015)
    c.text(0.1, 0.16, "+10%", 0.11, DGREEN)
@reg("savings_jar", "g")
def _(c, t):
    n = 0.5+0.5*math.sin(t*2)
    c.rect(-0.3, -0.34, 0.3, 0.4, LBLUE, INK, W_, 0.04)
    c.rect(-0.34, -0.42, 0.34, -0.32, GRAY, INK, 0.02, 0.03)
    for i in range(4):
        y = 0.3 - i*0.08
        c.ellipse(-0.12+i*0.08-0.1, y, 0.06, 0.04, GOLD, DGOLD, 0.012)
        c.ellipse(0.05+i*0.02, y, 0.06, 0.04, GOLD, DGOLD, 0.012)
    c.text(0, 0.0, "$", 0.18, DGOLD)
@reg("debt_chain", "f")
def _(c, t):
    for i in range(4):
        c.arc(-0.36+i*0.24, 0.0, 0.13, 0, 360, 0.05, GRAY)
        c.arc(-0.36+i*0.24, 0.05, 0.13, 0, 360, 0.05, GRAY)
@reg("pig_bank", "g")  # extra alias
def _(c, t):
    from props import PROPS as P
    P["piggy_bank"][0](c, t)

# ---------- extra tech / office / daily ----------
@reg("server", "g")
def _(c, t):
    for i in range(4):
        y = -0.4 + i*0.22
        c.rect(-0.4, y, 0.4, y+0.18, (60, 66, 84), INK, 0.02, 0.03)
        for j in range(3):
            k = (math.sin(t*4+i+j) > 0)
            c.circle(-0.28+j*0.1, y+0.09, 0.025, LGREEN if k else RED)
@reg("wifi", "f")
def _(c, t):
    for i in range(3):
        a = 0.1+i*0.12
        c.arc(0, 0.32, a*2.6, 200, 340, 0.04, BLUE)
    c.circle(0, 0.32, 0.05, BLUE)
@reg("cpu", "f")
def _(c, t):
    c.rect(-0.4,-0.4,0.4,0.4, (60, 66, 84), INK, W_, 0.04)
    for i in range(4):
        c.line([(-0.5,-0.3+i*0.2),(-0.4,-0.3+i*0.2)], 0.03, GOLD)
        c.line([(0.4,-0.3+i*0.2),(0.5,-0.3+i*0.2)], 0.03, GOLD)
    c.text(0, 0, "CPU", 0.28, GOLD)
@reg("monitor", "g")
def _(c, t):
    c.rect(-0.5,-0.44,0.5,0.16, INK, INK, W_, 0.04)
    c.rect(-0.44,-0.38,0.44,0.10, LBLUE)
    c.line([(0,0.16),(0,0.32)], 0.03, INK)
    c.rect(-0.2,0.32,0.2,0.4, INK)
@reg("tv", "g")
def _(c, t):
    c.rect(-0.48,-0.32,0.48,0.24, INK, INK, W_, 0.04)
    c.rect(-0.42,-0.26,0.42,0.18, LBLUE)
    c.rect(-0.05,0.24,0.05,0.36, INK)
    c.rect(-0.28,0.36,0.28,0.42, INK)
@reg("headphones", "f")
def _(c, t):
    c.arc(0,-0.1,0.36, 180, 360, 0.06, INK)
    c.rect(-0.42,-0.14,-0.3,0.16, INK, INK, 0.02, 0.03)
    c.rect(0.3,-0.14,0.42,0.16, INK, INK, 0.02, 0.03)
@reg("microphone", "f")
def _(c, t):
    c.rect(-0.14,-0.4,0.14,0.05, GRAY, INK, W_, 0.04)
    c.arc(0,0.05,0.28, 0, 180, 0.04, INK)
    c.line([(0,0.33),(0,0.48)], 0.03, INK)
@reg("camera", "f")
def _(c, t):
    c.rect(-0.42,-0.24,0.42,0.24, INK, INK, W_, 0.04)
    c.circle(0,0.0,0.16, GRAY, INK, 0.02)
    c.circle(0,0.0,0.08, LBLUE)
    c.rect(-0.3,-0.3,-0.16,-0.22, GRAY, INK, 0.015)
@reg("usb", "f")
def _(c, t):
    c.rect(-0.1,-0.4,0.1,-0.2, GRAY, INK, 0.02)
    c.rect(-0.24,-0.2,0.24,0.36, (60,66,84), INK, W_, 0.03)
    c.rect(-0.06,0.0,0.06,0.3, LGRAY)
@reg("folder", "f")
def _(c, t):
    c.rect(-0.4,-0.28,0.4,0.3, (250,200,90), INK, 0.03, 0.04)
    c.rect(-0.4,-0.4,-0.1,-0.26, (250,200,90), INK, 0.02, 0.03)
@reg("email_inbox", "f")
def _(c, t):
    for i in range(3):
        c.rect(-0.42,-0.36+i*0.22, 0.42,-0.18+i*0.22, WHITE, INK, 0.015, 0.03)
        c.text(-0.32,-0.27+i*0.22, "●", 0.1, RED, anchor="lm")

# ---------- people & things ----------
@reg("crown", "f")
def _(c, t):
    c.poly([(-0.36,-0.05),(-0.36,0.24),(0.36,0.24),(0.36,-0.05),(0.22,-0.05),(0.22,-0.24),
            (0.08,-0.05),(0.0,-0.3),(-0.08,-0.05),(-0.22,-0.24),(-0.22,-0.05)], GOLD, DGOLD, 0.03)
    c.circle(0,-0.1,0.05, RED)
@reg("star", "f")
def _(c, t):
    k = 1+0.06*math.sin(t*5)
    c.push(0,0,k)
    pts=[]
    for i in range(10):
        a = math.radians(-90+i*36)
        r = 0.42 if i%2==0 else 0.18
        pts.append((math.cos(a)*r, math.sin(a)*r))
    c.poly(pts, GOLD, DGOLD, 0.02)
    c.pop()
@reg("smiley", "f")
def _(c, t):
    c.circle(0,0,0.42, GOLD, DGOLD, 0.03)
    c.circle(-0.13,-0.08,0.045, INK)
    c.circle(0.13,-0.08,0.045, INK)
    c.arc(0,0.05,0.2, 30, 150, 0.03, INK)
@reg("skull", "f")
def _(c, t):
    c.circle(0,-0.08,0.3, WHITE, INK, 0.03)
    c.circle(-0.1,-0.12,0.06, INK)
    c.circle(0.1,-0.12,0.06, INK)
    c.rect(-0.16,0.14,0.16,0.36, WHITE, INK, 0.02)
    for i in (-0.06,0.06):
        c.line([(i,0.14),(i,0.36)], 0.015, INK)
@reg("ghost", "f")
def _(c, t):
    y = 0.03*math.sin(t*2)
    c.push(0,y,1)
    c.arc(0,-0.1,0.3, 180, 360, 0.03, WHITE)
    c.rect(-0.3,-0.1,0.3,0.28, WHITE)
    for i in range(3):
        c.poly([(-0.3+i*0.2,0.28),(-0.2+i*0.2,0.4),(-0.1+i*0.2,0.28)], WHITE)
    c.circle(-0.1,-0.1,0.04, INK)
    c.circle(0.1,-0.1,0.04, INK)
    c.pop()
@reg("alien", "f")
def _(c, t):
    c.ellipse(0,-0.08,0.34,0.3, LGREEN, DGREEN, 0.03)
    c.ellipse(-0.12,-0.1,0.06,0.09, INK)
    c.ellipse(0.12,-0.1,0.06,0.09, INK)
    c.line([(-0.1,0.14),(0.1,0.14)], 0.02, DGREEN)

# ---------- transport ----------
@reg("bus", "g")
def _(c, t):
    c.rect(-0.5,-0.28,0.5,0.28, GOLD, INK, W_, 0.03)
    for i in range(3):
        c.rect(-0.36+i*0.24,-0.2,-0.24+i*0.24,0.0, LBLUE, INK, 0.01)
    c.circle(-0.28,0.28,0.1, INK)
    c.circle(0.28,0.28,0.1, INK)
@reg("train", "g")
def _(c, t):
    c.rect(-0.5,-0.4,0.5,0.2, BLUE, INK, W_, 0.03)
    for i in range(4):
        c.rect(-0.4+i*0.24,-0.3,-0.28+i*0.24,-0.12, LBLUE, INK, 0.01)
    c.circle(-0.3,0.24,0.08, INK)
    c.circle(0.3,0.24,0.08, INK)
    c.line([(-0.5,0.2),(0.5,0.2)], 0.03, INK)
@reg("motorcycle", "g")
def _(c, t):
    c.circle(-0.3,0.24,0.14, INK)
    c.circle(0.3,0.24,0.14, INK)
    c.poly([(-0.3,0.1),(-0.1,-0.08),(0.1,-0.08),(0.3,0.1),(0.2,0.1),(-0.2,0.1)], RED, INK, 0.02)
    c.line([(0.24,0.1),(0.34,-0.18)], 0.03, INK)
@reg("bicycle", "g")
def _(c, t):
    c.circle(-0.3,0.24,0.16, None, INK, 0.025)
    c.circle(0.3,0.24,0.16, None, INK, 0.025)
    c.line([(-0.3,0.24),(0.0,-0.05),(0.3,0.24)], 0.02, INK)
    c.line([(0,-0.05),(0.0,0.24)], 0.02, INK)
@reg("skateboard", "g")
def _(c, t):
    c.rect(-0.42,0.16,0.42,0.24, INK, INK, W_, 0.03)
    c.circle(-0.28,0.34,0.06, GOLD)
    c.circle(0.28,0.34,0.06, GOLD)

# ---------- nature ----------
@reg("flower", "g")
def _(c, t):
    s = 0.02*math.sin(t*2)
    c.line([(0+s,-0.1),(0+s,0.5)], 0.03, DGREEN)
    for i in range(5):
        a = math.radians(i*72+t*20)
        c.ellipse(math.cos(a)*0.2, -0.1+math.sin(a)*0.2, 0.14, 0.14, PINK, None)
    c.circle(0,-0.1,0.1, GOLD)
@reg("cactus", "g")
def _(c, t):
    c.rect(-0.1,-0.5,0.1,0.5, GREEN, DGREEN, 0.03, 0.04)
    c.poly([(-0.1,-0.1),(-0.3,-0.1),(-0.3,-0.3),(-0.1,-0.3)], GREEN, DGREEN, 0.02)
    c.poly([(0.1,0.1),(0.3,0.1),(0.3,-0.1),(0.1,-0.1)], GREEN, DGREEN, 0.02)
@reg("tree_palm", "g")
def _(c, t):
    c.rect(-0.06,0.0,0.06,0.5, BROWN, INK, 0.02)
    for i in range(6):
        a = math.radians(i*60)
        c.poly([(0,0.0),(math.cos(a)*0.3,0.0+math.sin(a)*0.15),(math.cos(a)*0.4,math.sin(a)*0.05+0.1)], LGREEN, DGREEN, 0.02)
@reg("cloud_rain", "f")
def _(c, t):
    c.circle(-0.2,-0.1,0.2, WHITE, LGRAY, 0.02)
    c.circle(0.0,-0.2,0.24, WHITE, LGRAY, 0.02)
    c.circle(0.2,-0.1,0.2, WHITE, LGRAY, 0.02)
    for i in range(4):
        d = (t*2 + i*0.25) % 1
        c.line([(-0.2+i*0.15,0.05+d*0.3),(-0.22+i*0.15,0.15+d*0.3)], 0.02, BLUE)
@reg("lightning", "f")
def _(c, t):
    k = 0.5+0.5*math.sin(t*8)
    c.poly([(0.05,-0.42),(-0.14,0.0),(0.0,0.0),(-0.05,0.42),(0.2,-0.05),(0.05,-0.05)], GOLD if k>0.5 else DGOLD)
@reg("star_shape", "f")
def _(c, t):
    c.text(0,0, "★", 0.9, GOLD)
@reg("rainbow", "f")
def _(c, t):
    for i, col in enumerate([RED, ORANGE, GOLD, GREEN, BLUE, PURPLE]):
        c.arc(0,0.3, 0.42-i*0.06, 180, 360, 0.05, col)

# ---------- places / lifestyle ----------
@reg("school", "g")
def _(c, t):
    c.rect(-0.44,-0.06,0.44,0.5, (250,230,180), INK, W_)
    c.poly([(-0.5,-0.06),(0,-0.34),(0.5,-0.06)], RED, INK, W_)
    for i in range(3):
        c.rect(-0.3+i*0.2,0.1,-0.18+i*0.2,0.28, LBLUE, INK, 0.015)
    c.rect(-0.08,0.28,0.08,0.5, BROWN, INK, 0.015)
@reg("hospital", "g")
def _(c, t):
    c.rect(-0.42,-0.34,0.42,0.5, WHITE, INK, W_)
    c.rect(-0.5,-0.44,0.5,-0.32, RED, INK, 0.02)
    c.rect(-0.06,-0.5,0.06,-0.3, WHITE)
    c.rect(-0.14,-0.44,0.14,-0.36, WHITE)
    for i in range(3):
        c.rect(-0.3+i*0.2,0.1,-0.18+i*0.2,0.28, LBLUE, INK, 0.015)
@reg("gas_station", "g")
def _(c, t):
    c.rect(-0.4,-0.2,0.2,0.5, LGRAY, INK, W_, 0.03)
    c.rect(-0.34,-0.14,0.14,0.05, LBLUE, INK, 0.02)
    c.rect(0.1,-0.14,0.14,0.5, INK)
    c.line([(0.12,-0.1),(0.24,-0.1),(0.24,0.2),(0.34,0.2)], 0.03, INK)
@reg("gym", "g")
def _(c, t):
    c.rect(-0.44,-0.2,0.44,0.5, LGRAY, INK, W_, 0.03)
    c.rect(-0.44,-0.34,0.44,-0.18, RED, INK, 0.02)
    c.text(0,-0.26, "GYM", 0.12, WHITE)
@reg("restaurant", "g")
def _(c, t):
    c.rect(-0.44,-0.3,0.44,0.5, CREAM, INK, W_, 0.03)
    c.rect(-0.5,-0.44,0.5,-0.28, RED, INK, 0.02)
    c.text(0,-0.36, "CAFE", 0.1, WHITE)
    c.rect(-0.32,0.0,-0.08,0.3, LBLUE, INK, 0.02)
@reg("gift_card", "f")
def _(c, t):
    c.rect(-0.42,-0.26,0.42,0.26, PINK, INK, W_, 0.04)
    c.rect(-0.42,-0.26,0.42,-0.16, RED, INK, 0.02)
    c.text(0,0.05, "$25", 0.28, WHITE)

# ---------- misc ----------
@reg("piece_of_paper", "f")
def _(c, t):
    c.rect(-0.28,-0.36,0.28,0.36, WHITE, INK, W_, 0.02)
    for i in range(5):
        c.line([(-0.2,-0.24+i*0.12),(0.2,-0.24+i*0.12)], 0.015, LGRAY)
@reg("sticky_note", "f")
def _(c, t):
    c.rect(-0.28,-0.28,0.28,0.28, (255,235,120), INK, 0.02)
    for i in range(3):
        c.line([(-0.2,-0.15+i*0.14),(0.2,-0.15+i*0.14)], 0.015, INK)
@reg("clipboard", "f")
def _(c, t):
    c.rect(-0.3,-0.36,0.3,0.4, (170,120,80), INK, W_, 0.03)
    c.rect(-0.24,-0.32,0.24,0.34, WHITE, INK, 0.015)
    c.rect(-0.08,-0.42,0.08,-0.3, GRAY, INK, 0.02)
    for i in range(4):
        c.line([(-0.18,-0.2+i*0.12),(0.18,-0.2+i*0.12)], 0.015, LGRAY)
@reg("stamp", "f")
def _(c, t):
    c.rect(-0.3,0.0,0.3,0.32, (170,120,80), INK, W_, 0.03)
    c.arc(0,0.05,0.2, 180, 360, 0.02, INK)
    c.text(0,0.2, "PAID", 0.12, RED)
@reg("envelope_open", "f")
def _(c, t):
    c.rect(-0.44,-0.28,0.44,0.28, WHITE, INK, W_, 0.03)
    c.poly([(-0.44,-0.28),(0,0.05),(0.44,-0.28)], WHITE, INK, 0.025)
    c.rect(-0.2,-0.06,0.2,0.24, CREAM, INK, 0.015)
@reg("question_mark_big", "f")
def _(c, t):
    c.text(0,0, "?", 1.1, PURPLE)
@reg("exclamation_mark", "f")
def _(c, t):
    c.text(0,0, "!", 1.1, RED)
@reg("arrow_curved", "f")
def _(c, t):
    c.arc(0,0.1,0.3, 90, 270, 0.06, GREEN)
    c.poly([(-0.3,-0.2),(-0.4,-0.05),(-0.2,-0.05)], GREEN)
@reg("circle_progress", "f")
def _(c, t):
    k = (t*0.25) % 1
    c.arc(0,0,0.36, 0, 360, 0.06, LGRAY)
    c.arc(0,0,0.36, -90, -90+360*k, 0.07, GREEN)
    c.text(0,0.02, f"{int(k*100)}%", 0.22, INK)

# ---------- aliases to reach ~200 ----------
@reg("notebook", "f")
def _(c, t):
    c.rect(-0.28,-0.4,0.28,0.4, CREAM, INK, W_, 0.03)
    c.rect(-0.28,-0.4,-0.22,0.4, INK)
    for i in range(6):
        c.line([(-0.16,-0.3+i*0.12),(0.2,-0.3+i*0.12)], 0.01, LGRAY)
@reg("pen", "f")
def _(c, t):
    c.poly([(-0.3,-0.24),(-0.2,-0.24),(-0.2,0.24),(-0.3,0.24)], BLUE, INK, 0.015)
    c.poly([(-0.3,0.24),(-0.2,0.24),(-0.25,0.36)], INK)
@reg("pencil", "f")
def _(c, t):
    c.rect(-0.28,-0.3,-0.16,0.24, GOLD, DGOLD, 0.02)
    c.poly([(-0.28,0.24),(-0.16,0.24),(-0.22,0.38)], CREAM, INK, 0.015)
    c.rect(-0.28,-0.32,-0.16,-0.3, PINK)
@reg("hourglass_full", "f")  # alias
def _(c, t):
    from props import PROPS as P
    P["hourglass"][0](c, t)
@reg("trophy2", "f")  # alias
def _(c, t):
    from props import PROPS as P
    P["trophy"][0](c, t)
@reg("cash_bill", "f")
def _(c, t):
    c.rect(-0.5,-0.24,0.5,0.24, GREEN, DGREEN, W_, 0.04)
    c.circle(0,0,0.14, LGREEN, DGREEN, 0.02)
    c.text(0,0, "$", 0.24, DGREEN)
@reg("coin_stack_small", "g")
def _(c, t):
    for i in range(4):
        c.ellipse(0, 0.36-i*0.14, 0.16, 0.06, GOLD, DGOLD, 0.015)
@reg("star_badge", "f")
def _(c, t):
    for i in range(5):
        c.arc(-0.2+i*0.1,0.0,0.12,0,360,0.03, GOLD)
    c.rect(-0.3,0.16,0.3,0.4, GOLD, DGOLD, 0.02, 0.03)
@reg("medal_gold", "f")
def _(c, t):
    from props import PROPS as P
    P["medal"][0](c, t)
@reg("speedometer", "f")
def _(c, t):
    c.arc(0,0.1,0.4, 180, 360, 0.05, LGRAY)
    a = math.radians(180 + (t*40) % 180)
    c.line([(0,0.1),(math.cos(a)*0.32, 0.1+math.sin(a)*0.32)], 0.04, RED)
    c.circle(0,0.1,0.05, INK)
@reg("diamond_small", "f")
def _(c, t):
    c.poly([(0,-0.24),(0.2,0.0),(0,0.24),(-0.2,0.0)], CYAN, INK, 0.02)
@reg("crown_small", "f")
def _(c, t):
    from props import PROPS as P
    P["crown"][0](c, t)
@reg("dollar_coin", "f")
def _(c, t):
    from props import PROPS as P
    P["coin"][0](c, t)

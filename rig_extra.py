"""Extra actions + emotions. Imported by rig.py at bottom, auto-registers."""
import math
from rig import ACTIONS, EMO, S, ease

# ---------- 48 new actions (total becomes 68) ----------
def a_dance(t):
    return dict(au=160+S(t,2,30), al=170+S(t,2,40), bu=-160-S(t,2,30), bl=-170-S(t,2,40),
                lu=20+S(t,4,25), ru=-20-S(t,4,25), ll=S(t,4,20), rl=-S(t,4,20),
                torso=S(t,2,6), head=S(t,2,10), jump=0.03*abs(S(t,4)))
def a_kick(t):
    k = ease(min(1,t*2)); return dict(ru=-70*k, rl=-20*k, lu=10, ll=-5, au=30, al=50, bu=-30, bl=40, torso=10, head=5)
def a_punch(t):
    k = ease(min(1,t*3)); return dict(bu=-20-60*k, bl=-20-70*k, au=10, al=30, torso=-5, head=-3)
def a_push(t):    return dict(au=80, al=160, bu=80, bl=160, torso=15, head=8, lu=10, ru=-10, ll=-10, rl=-10)
def a_pull(t):    return dict(au=100, al=170, bu=100, bl=170, torso=-15, head=-8, lu=10, ru=-10, ll=-15, rl=-5)
def a_lift(t):    return dict(au=140, al=160, bu=-140, bl=-160, torso=-5, lu=10, ru=-10, ll=-3, rl=-3, jump=0.02*S(t,1))
def a_throw(t):
    k = ease(min(1,t*2)); return dict(bu=-140-40*k, bl=-160-30*k, au=20, al=40, torso=15, head=8, lu=5, ru=-15, ll=-5, rl=-20)
def a_catch(t):   return dict(au=120, al=140, bu=-120, bl=-140, torso=-5, lu=8, ru=-8, ll=-3, rl=-3)
def a_write(t):   return dict(au=40+S(t,3,3), al=110+S(t,3,5), bu=15, bl=60, head=15+S(t,.5,2), torso=5, hold="pencil")
def a_read(t):    return dict(au=50, al=125, bu=50, bl=125, head=20+S(t,.5,2), torso=5, hold="book")
def a_drink(t):   return dict(au=40, al=130+S(t,2,10), bu=-8, bl=-14, head=15, torso=3, hold="coffee")
def a_eat(t):     return dict(au=50+S(t,2,15), al=125+S(t,2,20), bu=-8, bl=-14, head=10, torso=3, hold="burger")
def a_sleep(t):   return dict(lie=0.9, torso=0, head=0, lu=4, ll=2, ru=-4, rl=-2, au=15, al=20, bu=-15, bl=-20)
def a_wake(t):
    k = ease(min(1,t*1.5)); return dict(torso=(1-k)*-20, head=-5*k, au=8+60*k, al=14+90*k, bu=-8-40*k, bl=-14-60*k, lu=4, ll=2, ru=-4, rl=-2, lie=1-k)
def a_yawn(t):    return dict(au=8+S(t,.5,3), al=140+S(t,.4,5), bu=-8, bl=-14, head=10, torso=3)
def a_stretch(t): return dict(au=165, al=170, bu=-165, bl=-170, torso=-3, head=-5, jump=0.01*S(t,1))
def a_scratch_head(t): return dict(au=25, al=155+S(t,3,15), bu=-8, bl=-14, head=12, torso=5)
def a_snap(t):    return dict(au=70, al=110, bu=-10, bl=-15, head=5, torso=3)
def a_thumbs_up(t):   return dict(au=45, al=90, bu=-8, bl=-14, head=8, torso=5)
def a_thumbs_down(t): return dict(au=8, al=14, bu=35, bl=90, head=-8, torso=2)
def a_cross_arms(t):  return dict(au=50, al=90, bu=-50, bl=-90, torso=3, head=5)
def a_hips(t):        return dict(au=15, al=140, bu=-15, bl=-140, torso=8, head=5)
def a_tap_foot(t):    return dict(lu=S(t,2,15), ll=S(t,2,15)-8, ru=-5, rl=-5, au=8, al=14, bu=-8, bl=-14, torso=2)
def a_pace(t):        return dict(lu=25*S(t,1), ll=25*S(t,1)-20, ru=-25*S(t,1), rl=-25*S(t,1)-20, au=-20*S(t,1), al=-20*S(t,1)+15, bu=20*S(t,1), bl=20*S(t,1)+15, dx=0.15*S(t,0.5), torso=3)
def a_lean(t):        return dict(torso=20, head=8, au=50, al=120, bu=-20, bl=-30, lu=15, ru=-15, ll=-10, rl=-10)
def a_crouch(t):      return dict(lu=70, ll=110, ru=70, rl=110, au=20, al=60, bu=-20, bl=-60, torso=20, head=10, jump=-0.1)
def a_kneel(t):       return dict(lu=80, ll=160, ru=90, rl=90, au=15, al=30, bu=-15, bl=-30, torso=8, head=5, jump=-0.15)
def a_bow(t):
    k = ease(min(1,t*1.5)); return dict(torso=40*k, head=30*k, au=15, al=60, bu=-15, bl=-60, lu=8, ru=-8, ll=-5, rl=-5)
def a_salute(t):      return dict(au=30, al=170, bu=-8, bl=-14, head=8, torso=5)
def a_high_five(t):   return dict(au=140, al=170, bu=-10, bl=-14, head=8, torso=3, jump=0.01*S(t,2))
def a_hug(t):         return dict(au=90, al=170, bu=-90, bl=-170, torso=-2, head=5)
def a_handshake(t):   return dict(au=80, al=155, bu=-80, bl=-155, torso=3, head=5)
def a_type(t):        return dict(au=55+S(t,10,3), al=130+S(t,10,5), bu=55-S(t,10,3), bl=130-S(t,10,5), head=20, torso=8)
def a_swipe(t):       return dict(au=45, al=100+S(t,2,20), bu=-8, bl=-14, head=15, torso=3, hold="phone")
def a_scroll(t):      return dict(au=45, al=120+S(t,3,10), bu=-8, bl=-14, head=18, torso=5, hold="phone")
def a_dial(t):        return dict(au=40, al=130, bu=-8, bl=-14, head=15, torso=3, hold="phone")
def a_texting(t):     return dict(au=55+S(t,10,2), al=130+S(t,10,3), bu=-10, bl=-14, head=20, torso=8, hold="phone")
def a_meditate(t):    return dict(lu=80, ll=100, ru=-80, rl=-100, au=90, al=120, bu=-90, bl=-120, torso=0, head=0)
def a_exercise(t):    return dict(au=100*S(t,2), al=140*S(t,2), bu=-100*S(t,2), bl=-140*S(t,2), lu=10+S(t,2,15), ru=-10-S(t,2,15), ll=-5, rl=-5, jump=0.02*abs(S(t,2)))
def a_march(t):       return dict(lu=30*S(t,1.5), ll=30*S(t,1.5)-20, ru=-30*S(t,1.5), rl=-30*S(t,1.5)-20, au=-25*S(t,1.5), al=-25*S(t,1.5)+20, bu=25*S(t,1.5), bl=25*S(t,1.5)+20, jump=0.03*abs(S(t,3)), torso=5)
def a_tiptoe(t):      return dict(lu=15*S(t,1), ll=15*S(t,1)-25, ru=-15*S(t,1), rl=-15*S(t,1)-25, au=-10*S(t,1), al=-10*S(t,1), bu=10*S(t,1), bl=10*S(t,1), jump=0.015, torso=-5)
def a_stumble(t):     return dict(torso=-20*S(t,2), lu=30+S(t,2,20), ru=-30-S(t,2,20), au=60+S(t,4,20), al=150, bu=-60-S(t,4,20), bl=-150, head=-15, dx=0.05*S(t,2))
def a_trip(t):
    k = ease(min(1,t*2)); return dict(torso=-90*k, head=-10*k, lu=15, ll=20, ru=-15, rl=-20, au=30-70*k, al=40-80*k, bu=-30+60*k, bl=-40+70*k, lie=k, dx=-0.05*k)
def a_spin(t):        return dict(dx=0.15*S(t,1), lu=15*S(t,2), ru=-15*S(t,2), ll=-10, rl=-10, au=30*S(t,2), al=30*S(t,2), bu=-30*S(t,2), bl=-30*S(t,2))
def a_hop(t):         return dict(jump=0.15*abs(S(t,1.5)), lu=10, ru=-10, ll=-5, rl=-5, au=60, al=60, bu=-60, bl=-60)
def a_skip(t):        return dict(lu=30*S(t,1.5), ll=30*S(t,1.5)-25, ru=-30*S(t,1.5), rl=-30*S(t,1.5)-25, au=-25*S(t,1.5), al=-25*S(t,1.5)+20, bu=25*S(t,1.5), bl=25*S(t,1.5)+20, jump=0.06*abs(S(t,3)), torso=5)
def a_cartwheel(t):
    k = ease(min(1,t/0.6)); return dict(dx=0.2*k, au=160, al=160, bu=-160, bl=-160, lu=10, ru=-10, ll=-5, rl=-5, jump=0.15*math.sin(math.pi*k))
def a_backflip(t):
    k = ease(min(1,t/0.6)); return dict(jump=0.25*math.sin(math.pi*k), lu=-30+60*k, ru=30-60*k, ll=-20, rl=20, au=160, al=170, bu=-160, bl=-170, torso=-5, head=-5)

ACTIONS.update({
    "dance": a_dance, "kick": a_kick, "punch": a_punch, "push": a_push, "pull": a_pull,
    "lift": a_lift, "throw": a_throw, "catch": a_catch, "write": a_write, "read": a_read,
    "drink": a_drink, "eat": a_eat, "sleep": a_sleep, "wake": a_wake, "yawn": a_yawn,
    "stretch": a_stretch, "scratch_head": a_scratch_head, "snap": a_snap, "thumbs_up": a_thumbs_up,
    "thumbs_down": a_thumbs_down, "cross_arms": a_cross_arms, "hips": a_hips, "tap_foot": a_tap_foot,
    "pace": a_pace, "lean": a_lean, "crouch": a_crouch, "kneel": a_kneel, "bow": a_bow,
    "salute": a_salute, "high_five": a_high_five, "hug": a_hug, "handshake": a_handshake,
    "type": a_type, "swipe": a_swipe, "scroll": a_scroll, "dial": a_dial, "texting": a_texting,
    "meditate": a_meditate, "exercise": a_exercise, "march": a_march, "tiptoe": a_tiptoe,
    "stumble": a_stumble, "trip": a_trip, "spin": a_spin, "hop": a_hop, "skip": a_skip,
    "cartwheel": a_cartwheel, "backflip": a_backflip,
})

# ---------- 40 new emotions (total becomes 50) ----------
EMO.update({
    "surprised":   dict(eye="wide", brow="up",   mouth="o",     extra=None),
    "disgusted":   dict(eye="dot",  brow="worry",mouth="wavy",  extra=None),
    "proud":       dict(eye="arc",  brow="up",   mouth="smirk", extra="sparkle"),
    "embarrassed": dict(eye="dot",  brow="worry",mouth="flat",  extra="sweat"),
    "curious":     dict(eye="wide", brow="up1",  mouth="flat",  extra="question"),
    "confused":    dict(eye="dot",  brow="worry",mouth="wavy",  extra="question"),
    "hopeful":     dict(eye="arc",  brow="up",   mouth="smile", extra=None),
    "disappointed":dict(eye="dot",  brow="worry",mouth="frown", extra=None),
    "grateful":    dict(eye="arc",  brow="up",   mouth="smile", extra="sparkle"),
    "jealous":     dict(eye="dot",  brow="angry",mouth="frown", extra=None),
    "guilty":      dict(eye="dot",  brow="worry",mouth="frown", extra=None),
    "bored":       dict(eye="bored",brow="none", mouth="flat",  extra=None), # POOR
    "determined":  dict(eye="dot",  brow="angry",mouth="grit",  extra=None),
    "relieved":    dict(eye="arc",  brow="up",   mouth="smile", extra=None),
    "anxious":     dict(eye="wide", brow="worry",mouth="wavy",  extra="sweat"),
    "calm":        dict(eye="arc",  brow="none", mouth="smile", extra=None),
    "nostalgic":   dict(eye="arc",  brow="up1",  mouth="smile", extra=None),
    "playful":     dict(eye="arc",  brow="up",   mouth="smirk", extra=None),
    "serious":     dict(eye="dot",  brow="angry",mouth="flat",  extra=None),
    "sarcastic":   dict(eye="bored",brow="up1",  mouth="smirk", extra=None), # RICH
    "sleepy":      dict(eye="arc",  brow="none", mouth="flat",  extra=None),
    "sick":        dict(eye="dot",  brow="worry",mouth="wavy",  extra=None),
    "hurt":        dict(eye="arc",  brow="worry",mouth="frown", extra="tear"),
    "betrayed":    dict(eye="dot",  brow="angry",mouth="frown", extra=None),
    "loved":       dict(eye="arc",  brow="up",   mouth="smile", extra="sparkle"),
    "lonely":      dict(eye="dot",  brow="worry",mouth="frown", extra=None),
    "inspired":    dict(eye="wide", brow="up",   mouth="big",   extra="sparkle"),
    "frustrated":  dict(eye="dot",  brow="angry",mouth="grit",  extra="steam"),
    "impatient":   dict(eye="dot",  brow="angry",mouth="flat",  extra=None),
    "overwhelmed": dict(eye="wide", brow="worry",mouth="o",     extra="sweat"),
    "peaceful":    dict(eye="arc",  brow="none", mouth="smile", extra=None),
    "suspicious":  dict(eye="dot",  brow="angry",mouth="flat",  extra=None),
    "sympathetic": dict(eye="dot",  brow="worry",mouth="smile", extra="tear"),
    "tired":       dict(eye="tired",brow="worry",mouth="flat",  extra=None), # POOR
    "eager":       dict(eye="wide", brow="up",   mouth="big",   extra=None),
    "awkward":     dict(eye="dot",  brow="worry",mouth="wavy",  extra="sweat"),
    "delighted":   dict(eye="arc",  brow="up",   mouth="big",   extra="sparkle"),
    "awestruck":   dict(eye="wide", brow="up",   mouth="o",     extra="sparkle"),
    "content":     dict(eye="arc",  brow="none", mouth="smile", extra=None),
    "mischievous": dict(eye="bored",brow="up1",  mouth="smirk", extra=None), # RICH
    # NEW ONES SPECIFICALLY FOR YOUR VIDEO
    "exhausted":   dict(eye="tired",brow="worry",mouth="frown", extra="sweat"), # VERY TIRED POOR
    "confident":   dict(eye="bored",brow="up1",  mouth="smirk", extra="sparkle"), # VERY CONFIDENT RICH
    "smug":        dict(eye="bored",brow="up1",  mouth="smirk", extra=None),      # RICH
})

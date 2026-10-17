"""Directs every scene. ONE stickman by default; TWO (Poor vs Rich) only when a line compares both.
No number badges on screen."""
import json, random, re
from llm import ask
import props as P
import props_extra
import rig
import rig_extra
from backgrounds import BACKGROUNDS
import config as C
from stickers import default_stickers_for
from formats import FORMATS

BATCH = 25
NUM = {w: i for i, w in enumerate(["zero","one","two","three","four","five","six","seven","eight","nine","ten"])}
LABEL_RE = re.compile(r"(?:^|[.!?]\s+)(number|day|myth|part|scenario|mistake)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s*[.:]", re.I)

KEYWORDS = {
    "money":"money_stack","cash":"money_stack","rich":"bills_rain","poor":"cross_mark","wealth":"bills_rain",
    "save":"piggy_bank","debt":"credit_card","bank":"bank","invest":"chart_up","stock":"candles","market":"candles",
    "business":"store","buy":"shopping_cart","spend":"shopping_bag","house":"house","car":"car","job":"briefcase",
    "work":"briefcase","mindset":"brain","brain":"brain","habit":"calendar","goal":"target","success":"trophy",
    "mistake":"cross_mark","stop":"cross_mark","risk":"warning","warning":"warning","secret":"lock","key":"key",
    "time":"clock","wait":"hourglass","start":"rocket","plan":"contract","free":"gift","tree":"tree","money_bag":"cash_bag",
    "subscribe":"btn_subscribe","like":"btn_like","bell":"btn_bell","comment":"btn_comment",
}
CROWD_WORDS = ["people","everyone","most people","millions","friends","family","society"]
POS = ["win","success","rich","wealth","grow","profit","free","happy","freedom","love"]
NEG = ["lose","debt","broke","poor","mistake","wrong","fail","stress","trap","danger","never","stop"]
POOR_W = ["poor","broke","debt","struggle","struggling","paycheck to paycheck"]
RICH_W = ["rich","wealthy","wealth","millionaire"]

def annotate_items(scenes):
    """No on-screen number/label badges (no 'DAY 3', '#5'). Videos are idea-driven, not number-driven."""
    for sc in scenes:
        sc["item_start"] = False
        sc["item_label"] = ""

def _has(text, w): return re.search(r"\b" + re.escape(w) + r"\b", text) is not None

def guess_props(text):
    t = text.lower(); out = []
    for w, p in KEYWORDS.items():
        if p not in out and _has(t, w): out.append(p)
    return out[:3]

def guess_emotion(text):
    t = text.lower()
    if "!" in text: return "excited"
    if "?" in text: return "thinking"
    neg = sum(_has(t, w) for w in NEG); pos = sum(_has(t, w) for w in POS)
    if neg > pos: return random.choice(["worried","sad","shocked","angry"])
    if pos > neg: return random.choice(["happy","excited","confident"])
    return random.choice(["neutral","confident","thinking"])

def guess_who(text):
    """'poor', 'rich', 'both' (comparison) or None."""
    t = text.lower()
    p = any(_has(t, w) for w in POOR_W); r = any(_has(t, w) for w in RICH_W)
    if p and r: return "both"
    if p: return "poor"
    if r: return "rich"
    return None

def guess_bg(text, prev, pool):
    t = text.lower()
    for words, bg in [(["night","sleep","bed"],"night"), (["home","house","room","rent"],"room"),
                      (["office","job","boss","work"],"office"), (["city","street","car"],"city"),
                      (["money","cash","rich"],"money"), (["park","nature","walk"],"park")]:
        if bg in pool and any(_has(t, w) for w in words): return bg
    return prev or random.choice(pool)

def _fix(sc, d, prev, pool):
    text = sc["text"]
    bg = d.get("bg") if d.get("bg") in BACKGROUNDS else None
    emo = d.get("emotion") if d.get("emotion") in rig.EMO else None
    act = d.get("action") if d.get("action") in rig.ACTIONS else None
    pr = [p for p in (d.get("props") or []) if isinstance(p, str)][:3]
    emo = emo or guess_emotion(text)
    if not act or (prev and act == prev.get("action")):
        choices = ["idle","point","think","shrug","walk"]
        act = random.choice([a for a in choices if not prev or a != prev.get("action")] or ["idle"])
    is_text = d.get("mode") == "text" or (len(text.split()) <= 10 and random.random() < C.TEXT_SCENE_CHANCE)
    stickers = d.get("stickers") if isinstance(d.get("stickers"), list) else None
    if stickers is None and random.random() < C.STICKER_CHANCE:
        s = default_stickers_for(text)
        if s: stickers = [{"text": s[0], "color": s[1], "x": 0.5, "y": 0.12, "size": 0.11}]
    g = guess_who(text)
    who = d.get("who") if d.get("who") in ("poor", "rich") else (g if g in ("poor", "rich") else None)
    dual = bool(d["dual"]) if "dual" in d else (g == "both")
    if dual:
        who = None
    sc.update(
        bg=bg or guess_bg(text, prev["bg"] if prev else None, pool),
        emotion=emo, action=act,
        props=pr or guess_props(text),
        crowd=bool(d.get("crowd")) or (any(_has(text.lower(), w) for w in CROWD_WORDS) and random.random() < 0.5),
        mode="text" if is_text else "scene",
        text_overlay=d.get("text_overlay") if is_text else None,
        stickers=stickers,
        who=who,
        dual=dual,
        dual_labels=["POOR", "RICH"],
        dual_action_2=d.get("dual_action_2") if d.get("dual_action_2") in rig.ACTIONS else "celebrate",
        dual_emotion_2=d.get("dual_emotion_2") if d.get("dual_emotion_2") in rig.EMO else "happy"
    )

def _parse(raw):
    raw = re.sub(r"```(json)?", "", raw)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m: return None
    for cand in (m.group(0), re.sub(r",\s*([\]}])", r"\1", m.group(0))):
        try:
            data = json.loads(cand)
            return [d for d in data if isinstance(d, dict) and "i" in d]
        except Exception: continue
    return None

def plan_scenes(scenes, topic, fmt=None):
    annotate_items(scenes)
    pool = [b for b in FORMATS.get(fmt, {}).get("bgs", []) if b in BACKGROUNDS] or list(BACKGROUNDS)
    prev = None
    for b0 in range(0, len(scenes), BATCH):
        batch = scenes[b0:b0 + BATCH]
        lines = "\n".join(f"{b0 + j}. {s['text']}" for j, s in enumerate(batch))
        prompt = (
            f"You are the director of a Rich vs Poor Psychology stickman video titled: {topic}\n"
            "For each numbered narration line, choose how the animated scene looks.\n"
            f"Backgrounds you may use: {', '.join(pool)}\n"
            f"Emotions: {', '.join(rig.EMO)}\n"
            f"Actions: {', '.join(rig.ACTIONS)}\n"
            f"Props: {', '.join(P.catalog())}\n"
            "Rules:\n"
            "- Props must show the main things mentioned.\n"
            "- Keep the same background as the previous line unless the place changes.\n"
            "- Vary actions. Never repeat the same action on two lines in a row.\n"
            "- If the line is a strong stat or CTA, set \"mode\":\"text\" and give \"text_overlay\" (max 12 words).\n"
            "- Add a sticker for punch words (FREE, NEVER, 100%).\n"
            "- Default is ONE big stickman. Set \"dual\":true ONLY when the line directly compares poor vs rich at the same time. "
            "In dual scenes the LEFT is POOR (use action/emotion) and the RIGHT is RICH (use dual_action_2/dual_emotion_2).\n"
            "- In single scenes set \"who\":\"poor\" if the line is about the poor person (red shirt), \"rich\" if about the rich person (green shirt), "
            "or \"none\" for neutral lines (blue shirt). Match the emotion: poor = worried/sad/shocked, rich = confident/happy.\n"
            "Return ONLY a JSON array like [{\"i\":0,\"bg\":\"city\",\"emotion\":\"shocked\",\"action\":\"scared\",\"props\":[\"bank\"],\"crowd\":false,\"mode\":\"scene\",\"stickers\":[],\"dual\":false,\"who\":\"poor\",\"dual_action_2\":\"celebrate\",\"dual_emotion_2\":\"happy\"}]\n"
            f"Previous background: {prev['bg'] if prev else 'none'}\nLines:\n{lines}"
        )
        got = {}
        try:
            raw = ask(prompt, max_tokens=3500, temperature=0.5,
                      validate=lambda t: (lambda p: p is not None and len(p) >= 0.6 * len(batch))(_parse(t)))
            for d in _parse(raw):
                try: got[int(d["i"])] = d
                except Exception: pass
        except Exception as e:
            print(f"[planner] batch {b0} failed ({e}); using keyword fallback")
        for j, sc in enumerate(batch):
            try:
                _fix(sc, got.get(b0 + j, {}), prev, pool)
            except Exception as e:
                print(f"[planner] scene {b0 + j} fix failed ({type(e).__name__}: {e}); using safe defaults")
                sc.update(bg=(prev["bg"] if prev else pool[0]), emotion="neutral", action="idle", props=[], crowd=False,
                          mode="scene", text_overlay=None, stickers=[], who=None, dual=False,
                          dual_labels=["POOR", "RICH"], dual_action_2="celebrate", dual_emotion_2="happy")
            prev = sc
    print(f"[planner] {len(scenes)} scenes planned")

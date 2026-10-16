"""Directs every scene. Forces dual stickmen (Poor vs Rich) for the psychology channel."""
import json, random, re
from llm import ask
import props as P
import props_extra
import rig
import rig_extra
from backgrounds import BACKGROUNDS
import config as C
from stickers import default_stickers_for

BATCH = 25
NUM = {w: i for i, w in enumerate(["zero","one","two","three","four","five","six","seven","eight","nine","ten"])}
LABEL_RE = re.compile(r"(?:^|[.!?]\s+)(number|day)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s*[.:]", re.I)

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

def annotate_items(scenes):
    cur = ""
    for sc in scenes:
        m = LABEL_RE.search(sc["text"])
        sc["item_start"] = bool(m)
        if m:
            n = m.group(2).lower(); n = NUM.get(n, n)
            cur = f"DAY {n}" if m.group(1).lower() == "day" else f"#{n}"
        sc["item_label"] = cur

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

def guess_bg(text, prev):
    t = text.lower()
    for words, bg in [(["night","sleep","bed"],"night"), (["home","house","room","rent"],"room"),
                      (["office","job","boss","work"],"office"), (["city","street","car"],"city"),
                      (["money","cash","rich"],"money"), (["park","nature","walk"],"park")]:
        if any(_has(t, w) for w in words): return bg
    return prev or random.choice(BACKGROUNDS)

def _fix(sc, d, prev):
    text = sc["text"]
    bg = d.get("bg") if d.get("bg") in BACKGROUNDS else None
    emo = d.get("emotion") if d.get("emotion") in rig.EMO else None
    act = d.get("action") if d.get("action") in rig.ACTIONS else None
    pr = [p for p in (d.get("props") or []) if isinstance(p, str)][:3]
    emo = emo or guess_emotion(text)
    if not act or (prev and act == prev.get("action")):
        pool = ["idle","point","think","shrug","walk"]
        act = random.choice([a for a in pool if not prev or a != prev.get("action")] or ["idle"])
    is_text = d.get("mode") == "text" or (len(text.split()) <= 10 and random.random() < C.TEXT_SCENE_CHANCE)
    stickers = d.get("stickers") if isinstance(d.get("stickers"), list) else None
    if stickers is None and random.random() < C.STICKER_CHANCE:
        s = default_stickers_for(text)
        if s: stickers = [{"text": s[0], "color": s[1], "x": 0.5, "y": 0.20, "size": 0.11}]
    sc.update(
        bg=bg or guess_bg(text, prev["bg"] if prev else None),
        emotion=emo, action=act,
        props=pr or guess_props(text),
        crowd=bool(d.get("crowd")) or (any(_has(text.lower(), w) for w in CROWD_WORDS) and random.random() < 0.5),
        mode="text" if is_text else "scene",
        text_overlay=d.get("text_overlay") if is_text else None,
        stickers=stickers,
        dual=True,  # <-- FORCED for this channel
        dual_labels=["POOR", "RICH"], # <-- FORCED
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

def plan_scenes(scenes, topic):
    annotate_items(scenes)
    prev = None
    for b0 in range(0, len(scenes), BATCH):
        batch = scenes[b0:b0 + BATCH]
        lines = "\n".join(f"{b0 + j}. {s['text']}" for j, s in enumerate(batch))
        prompt = (
            f"You are the director of a Rich vs Poor Psychology stickman video titled: {topic}\n"
            "For each numbered narration line, choose how the animated scene looks.\n"
            f"Backgrounds: {', '.join(BACKGROUNDS)}\n"
            f"Emotions: {', '.join(rig.EMO)}\n"
            f"Actions: {', '.join(rig.ACTIONS)}\n"
            f"Props: {', '.join(P.catalog())}\n"
            "Rules:\n"
            "- Props must show the main things mentioned.\n"
            "- Keep the same background as the previous line unless the place changes.\n"
            "- Vary actions. Never repeat the same action on two lines in a row.\n"
            "- If the line is a strong stat or CTA, set \"mode\":\"text\" and give \"text_overlay\" (max 12 words).\n"
            "- Add a sticker for punch words (FREE, NEVER, 100%).\n"
            "- The LEFT stickman is always the POOR. The RIGHT stickman is always the RICH.\n"
            "Return ONLY a JSON array like [{\"i\":0,\"bg\":\"city\",\"emotion\":\"shocked\",\"action\":\"scared\",\"props\":[\"bank\"],\"crowd\":false,\"mode\":\"scene\",\"stickers\":[],\"dual_action_2\":\"celebrate\",\"dual_emotion_2\":\"happy\"}]\n"
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
            _fix(sc, got.get(b0 + j, {}), prev)
            prev = sc
    print(f"[planner] {len(scenes)} scenes planned")

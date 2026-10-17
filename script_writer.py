"""Rich vs Poor Psychology script writer.
No forced numbers or labels. Each video has its own angle, hook style and ending style (see formats.py)."""
import random, re, time
from llm import ask
from config import SPECS
from formats import FORMATS, HOOK_STYLES, ENDINGS

SYSTEM = (
    "You are the voice of a YouTube channel about the Psychology of Rich vs Poor. "
    "Viewers are in the USA, UK, Canada and Australia. "
    "You talk like a real person speaking to ONE friend across a table, not like a presenter or an AI. "
    "Use simple words, contractions (you're, don't, it's), and short punchy sentences mixed with the occasional longer one. "
    "Sound alive: it is fine to use fragments. Like this. Use 'you' a lot. Be specific and concrete: real moments, small scenes, real numbers like $4.99 or a 2am phone scroll. "
    "Show what a poor mindset does and what a rich mindset does. Make the contrast emotional and a little uncomfortable. "
    "Never invent studies, statistics, or expert names. Never give personal financial advice or tell people what to buy. "
    "Never label or number parts out loud (no 'number one', 'day three', 'part two', 'first, second, third' lists) unless the idea truly needs it. "
    "Move between ideas with natural spoken transitions. "
    "Never use phrases like: in today's world, let's dive in, let's explore, game changer, it's important to, delve, furthermore, in conclusion, at the end of the day, unlock, mindset shift. "
    "Output ONLY the words the narrator says. No labels, no markdown, no brackets. "
    "Never start with Hello, Welcome, In this video, or Have you ever."
)
FORBIDDEN = ("hello", "welcome", "in this video", "have you ever", "hi ", "hey ", "today we", "today i", "in today")
ROBOTIC = ("let's dive", "lets dive", "let's explore", "in today's", "game changer", "game-changer", "delve",
           "furthermore", "in conclusion", "at the end of the day", "it's important to", "it is important to",
           "unlock your", "mindset shift", "buckle up", "without further ado")
LABEL = re.compile(r"^\s*(voice|narrator|host|title|scene\s*\d*|intro|outro|hook|script|section\s*\d*)\s*[:\-–].*$", re.I)
BARE = re.compile(r"^\s*#*\s*(part|scene|section|chapter|beat)\s*\d+\s*$", re.I)
PREAMBLE = re.compile(r"^\s*(sure|certainly|here is|here's|okay|of course)\b.*:\s*$", re.I)
SPOKEN_LABEL = re.compile(r"\b(number|day|part|beat|step|point|myth|scenario|mistake)\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b[.:]?\s*", re.I)

HOOK_GUIDE = (
    "THE HOOK MUST BE A HIGH-CURIOSITY PSYCHOLOGICAL HOOK. The viewer must feel they cannot leave without the answer.\n"
    "Rules: the FIRST sentence is 12 words or fewer. No greeting, no intro, no 'have you ever'. "
    "Talk straight to 'you'. Make them feel a little caught and very curious. "
    "Hold back the answer, open a loop you only close at the end. Never sound like a presenter."
)

CTA_MID_OPTIONS = [
    "Quick pause. If this is hitting home, hit subscribe and tell me in the comments which country you're watching from. I read them. Okay. Back to it.",
    "Real quick. If you're still here, you're already thinking different. Subscribe so you don't miss the next one. Now, where were we.",
    "Hold on a second. Drop a comment and tell me which part of this sounds like you. No judgment. Okay, keep going.",
    "Before I go on. A like helps more than you think. Thank you. Now, stay with me.",
]

def _fmt(job):
    return FORMATS.get(job.get("fmt"), FORMATS["truth"])

def _hook_text(job):
    return HOOK_STYLES.get(job.get("hook_style"), "") or _fmt(job)["hook"]

def _end_text(job):
    return ENDINGS.get(job.get("ending"), ENDINGS["question"])

def _clean(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?", " ", text)
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"[*_`]", "", ln).lstrip("# ")
        if LABEL.match(ln) or BARE.match(ln) or PREAMBLE.match(ln): continue
        ln = re.sub(r"^\s*[-•]\s+", "", ln)
        lines.append(ln)
    text = " ".join(lines)
    text = re.sub(r"[*_#`>~|]", "", text).replace("—", ", ").replace("–", ", ")
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r",\s*,+", ",", text)
    return re.sub(r"\s+", " ", text).strip().strip('"')

def wc(t): return len(t.split())
def _bad_opener(t): return t.lower().lstrip().startswith(FORBIDDEN)
def _robotic(t):
    low = t.lower()
    return any(p in low for p in ROBOTIC)
def _labelled(t):
    """True if the narration reads out 'number one', 'day three' etc. as a label at the start of a sentence."""
    return re.search(r"(^|[.!?]\s+)(number|day|part|beat|step|myth|scenario|mistake)\s+(one|two|three|four|five|six|seven|eight|nine|ten)\b", t, re.I) is not None
def _first_len(t):
    first = re.split(r"(?<=[.!?])\s+", t.strip())[0]
    return wc(first)

def _outline(job):
    n = job["beats"]
    prompt = (f"Video title: {job['title']}\n"
              f"{_fmt(job)['outline'].format(n=n)}\n"
              "One line each: a short name, a dash, then one sentence. "
              f"Numbered 1 to {n} (the numbers are only for planning, the viewer never hears them). Output only the numbered list.")
    pat = re.compile(r"^\s*\d+[.)]\s*(.+)$", re.M)
    raw = ask(prompt, max_tokens=900, validate=lambda t: len(pat.findall(t)) >= n)
    return [m.strip() for m in pat.findall(raw)][:n]

def _chunk(prompt, lo, hi, hook=False, so_far=""):
    ctx = ""
    if so_far:
        ctx = ('The narration so far ends with: "' + " ".join(so_far.split()[-110:]) + '"\n'
               "Continue smoothly. Do not repeat anything already said.\n")
    full = f"{prompt}\n\n{ctx}Output ONLY the spoken narration."
    def ok(raw, lo=lo):
        c = _clean(raw)
        if not (lo <= wc(c) <= hi): return False
        if hook and (_bad_opener(c) or _robotic(c) or _first_len(c) > 16): return False
        return not _robotic(c) and not _labelled(c)
    for attempt in range(3):
        try:
            loose = (lambda raw: max(50, lo // 2) <= wc(_clean(raw)) <= hi * 2)
            return _clean(ask(full, system=SYSTEM, max_tokens=1800, validate=ok if attempt == 0 else loose))
        except RuntimeError:
            print(f"[script] chunk failed (attempt {attempt + 1}), waiting"); time.sleep(20)
    return None

def _strip_labels(t):
    """Safety net: remove spoken labels like 'Number five.' that the AI sometimes adds anyway."""
    return re.sub(r"(^|(?<=[.!?]\s))(number|day|part|beat|step|myth|scenario|mistake)\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s*[.:]\s*", r"\1", t, flags=re.I).strip()

def _pick_hook(job, intro_w):
    """Write 4 different hook openings in the chosen hook style, let the AI judge pick the most gripping one."""
    F = _fmt(job)
    base = (f"Video title: {job['title']}\n"
            f"Write FOUR different OPENINGS for this video, each about {intro_w} words, each with a different first sentence.\n"
            f"{HOOK_GUIDE}\n"
            f"Hook style to use: {_hook_text(job)}\n"
            f"Angle of this video: {F['hook']}\n"
            f"Each opening must also make clear that {F['promise']}, "
            "and end with a short, natural, spoken line that leans into the first idea.\n"
            "Do NOT list the ideas. Do NOT say subscribe, like, or comment. Do not use numbered labels.\n"
            "Separate the four openings with a line that contains only: -----\n"
            "Output ONLY the four openings.")
    def parse(raw):
        parts = [_clean(p) for p in re.split(r"\n\s*-{3,}\s*\n", raw or "")]
        return [p for p in parts if 60 <= wc(p) <= 360]
    try:
        raw = ask(base, system=SYSTEM, max_tokens=2600, temperature=0.95, validate=lambda t: len(parse(t)) >= 2)
    except RuntimeError:
        return None
    cands = [p for p in parse(raw) if not _bad_opener(p) and not _robotic(p)] or parse(raw)
    if not cands: return None
    if len(cands) == 1: return cands[0]
    listing = "\n\n".join(f"OPTION {i + 1}:\n{c}" for i, c in enumerate(cands))
    try:
        ans = ask("You judge YouTube hooks. Which opening would make a stranger scrolling at night stop and keep watching to the end? "
                  "Prefer the one with the strongest curiosity gap, a specific moment, and the most human voice. "
                  f"Reply with ONLY the option number.\n\n{listing}", max_tokens=10, temperature=0.2,
                  validate=lambda t: re.search(r"\d", t) is not None)
        k = int(re.search(r"\d", ans).group(0)) - 1
        if 0 <= k < len(cands): return cands[k]
    except Exception:
        pass
    return cands[0]

def write_long(job, outline=None):
    spec, n, F = SPECS["long"], job["beats"], _fmt(job)
    items = outline or _outline(job)
    intro_w, outro_w = 200, 200
    beat_w = max(110, min(340, (spec["words_target_total"] - intro_w - outro_w) // n))
    parts = []
    opening = _pick_hook(job, intro_w)
    if not opening:
        opening = _chunk(
            f"Video title: {job['title']}\n"
            f"Write the OPENING (about {intro_w} words). This is the first thing the viewer hears.\n{HOOK_GUIDE}\n"
            f"Hook style to use: {_hook_text(job)}\nAngle of this video: {F['hook']}\n"
            f"Make clear that {F['promise']}.\n"
            "End with a short natural spoken line that leans into the first idea.\n"
            "Do NOT list the ideas. Do NOT say subscribe, like, or comment.",
            120, 540, hook=True)
    if not opening: raise RuntimeError("Could not write the opening")
    parts.append(_strip_labels(opening))
    for i, item in enumerate(items):
        last = i == len(items) - 1
        txt = None
        for _ in range(2):
            txt = _chunk(
                f"Video title: {job['title']}\n"
                + F["section"].format(item=item, w=beat_w) + "\n"
                "Start with a natural spoken transition from what was just said. Do NOT say a number or label at the start.\n"
                + ("This is the last idea, so land it hard and do not tease a next one." if last else
                   "Then end with one short curiosity line that makes them need what comes next, without naming it."),
                max(60, beat_w // 2), int(beat_w * 2.4), so_far=" ".join(parts))
            if txt: break
        if txt: parts.append(_strip_labels(txt))
        if i == len(items) // 2: parts.append(random.choice(CTA_MID_OPTIONS))
    final = _chunk(
        f"Video title: {job['title']}\nWrite the FINAL section (about {outro_w} words).\n"
        f"Ending style: {_end_text(job)}\n"
        "Recap in two short sentences. Give one simple thing the viewer can start today. "
        "Somewhere in it, ask in your own fresh words (never the same phrasing as other videos) for a subscribe, "
        "and ask them to comment which country they are watching from.",
        80, 540, so_far=" ".join(parts))
    if final: parts.append(_strip_labels(final))
    text = " ".join(parts)
    extra = 0
    while wc(text) < spec["words_hard_min"] and extra < 3:
        extra += 1
        bonus = _chunk(
            f"Video title: {job['title']}\nWrite one more section (about 350 words) that tells a short real-life story of two people, "
            "one with a poor mindset and one with a rich mindset, facing the same money moment and choosing differently. "
            "Do not say subscribe. Do not wrap up the video.",
            150, 800, so_far=" ".join(parts[:-1]) if final else " ".join(parts))
        if not bonus: break
        if final:
            parts.insert(len(parts) - 1, _strip_labels(bonus))
        else:
            parts.append(_strip_labels(bonus))
        text = " ".join(parts)
    if wc(text) < spec["words_hard_min"]: raise RuntimeError(f"Long script too short ({wc(text)} words)")
    print(f"[script] long ({job.get('fmt')}, hook={job.get('hook_style')}, end={job.get('ending')}): {wc(text)} words")
    return text

def write_short(job, outline=None):
    spec, F = SPECS["short"], _fmt(job)
    lo, hi = spec["words_target"]; alo, ahi = spec["words_accept"]
    items = outline or _outline(job)
    plan = "\n".join(f"- {it}" for it in items)
    last = None
    for attempt in range(3):
        strict = "" if attempt == 0 else f" STRICT: between {lo} and {hi} words."
        prompt = (f"Video title: {job['title']}\nWrite a YouTube Short of about {(lo + hi) // 2} words.\n"
                  f"{HOOK_GUIDE}\n"
                  f"Hook style to use: {_hook_text(job)}\nAngle of this video: {F['hook']}\n"
                  "The first 2 sentences are the hook and must stop the scroll. Then move through these ideas in order, fast and punchy, "
                  "with natural spoken transitions and NO numbered labels:\n"
                  f"{plan}\n"
                  f"For each idea: {F['short']} Keep the biggest surprise for the end.\n"
                  f"Ending style: {_end_text(job)} Include a short ask to subscribe in fresh words.{strict}\n"
                  "Output ONLY the spoken narration.")
        try:
            raw = ask(prompt, system=SYSTEM, max_tokens=900, temperature=0.9,
                      validate=lambda t: alo <= wc(_clean(t)) <= ahi and not _bad_opener(_clean(t)) and not _robotic(_clean(t)))
        except RuntimeError: time.sleep(20); continue
        last = _strip_labels(_clean(raw))
        if alo <= wc(last) <= ahi: break
    if not last: raise RuntimeError("Could not write the short script")
    print(f"[script] short ({job.get('fmt')}, hook={job.get('hook_style')}, end={job.get('ending')}): {wc(last)} words")
    return last

def write(job, outline=None):
    return write_long(job, outline) if job["kind"] == "long" else write_short(job, outline)

def get_outline(job):
    return _outline(job)

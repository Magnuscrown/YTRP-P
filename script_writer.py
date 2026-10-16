"""Rich vs Poor Psychology script writer. Always starts with the POOR mindset, then contrasts with the RICH."""
import re, time
from llm import ask
from config import SPECS

NUMW = ["zero","one","two","three","four","five","six","seven","eight","nine","ten"]

SYSTEM = (
    "You are the narrator of a YouTube channel about the Psychology of Rich vs Poor. "
    "Viewers are in the USA, UK, Canada and Australia. "
    "Write in simple, warm, plain English - like explaining to a 10-year-old. Short sentences. No jargon. "
    "For every item, FIRST describe what a poor person does or thinks. THEN describe what a rich person does or thinks. "
    "Make the contrast feel real and emotional. "
    "Output ONLY the words the narrator says. No labels, no markdown, no brackets. "
    "Never start with Hello, Welcome, In this video, or Have you ever."
)
FORBIDDEN = ("hello","welcome","in this video","have you ever","hi ","hey ")
LABEL = re.compile(r"^\s*(voice|narrator|host|title|scene\s*\d*|intro|outro|hook|script|section\s*\d*)\s*[:\-–].*$", re.I)
BARE = re.compile(r"^\s*#*\s*(part|scene|section|chapter)\s*\d+\s*$", re.I)
PREAMBLE = re.compile(r"^\s*(sure|certainly|here is|here's|okay|of course)\b.*:\s*$", re.I)

CTA_OPEN_END = "Now let's start with the first one."
CTA_MID = ("Before we go on. If this is helping you, hit subscribe, turn on the bell, "
           "and give the video a like. Also comment which country you are watching from. I read every single one. "
           "Now, back to the list.")
CTA_END = ("If this helped you, subscribe, hit the bell, and comment which country you are watching from. "
           "I will see you in the next one.")

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

def labels(job):
    n = job["n"]
    nums = list(range(n, 0, -1)) if job["order"] == "desc" else list(range(1, n + 1))
    return [f"{job['label']} {NUMW[k]}." for k in nums]

def _outline(job):
    n = job["n"]
    prompt = (f"Video title: {job['title']}\n"
              f"List exactly {n} distinct, specific items for a Rich vs Poor psychology video. "
              f"The last one must be the most surprising. One line each: a short name, a dash, then one sentence. "
              f"Numbered 1 to {n}. Output only the numbered list.")
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
        c = _clean(raw); return lo <= wc(c) <= hi and not (hook and _bad_opener(c))
    for attempt in range(3):
        try:
            loose = (lambda raw: max(50, lo // 2) <= wc(_clean(raw)) <= hi * 2)
            return _clean(ask(full, system=SYSTEM, max_tokens=1800, validate=ok if attempt == 0 else loose))
        except RuntimeError:
            print(f"[script] chunk failed (attempt {attempt + 1}), waiting"); time.sleep(20)
    return None

def write_long(job, outline=None):
    spec, n = SPECS["long"], job["n"]
    labs = labels(job); items = outline or _outline(job)
    intro_w, outro_w = 220, 200
    item_w = max(110, min(340, (spec["words_target_total"] - intro_w - outro_w) // n))
    parts = []
    opening = _chunk(
        f"Video title: {job['title']}\n"
        f"Write the OPENING (about {intro_w} words). This is the first thing the viewer hears.\n"
        f"Start with a strong curiosity hook in the very first sentence.\n"
        f"Tell them there are {n} items in this video and the last one is the one most people never expect.\n"
        f"Then say: \"{CTA_OPEN_END}\"\n"
        "Do NOT list the items yet. Do NOT say subscribe, like, or comment.",
        150, 540, hook=True)
    if not opening: raise RuntimeError("Could not write the opening")
    parts.append(opening)
    for i, (lab, item) in enumerate(zip(labs, items)):
        last = i == n - 1
        txt = _chunk(
            f"Video title: {job['title']}\nWrite the section for this item (about {item_w} words): {item}\n"
            f'Start with exactly "{lab}" as its own short sentence.\n'
            "FIRST explain what the POOR person does or thinks about this.\n"
            "THEN explain what the RICH person does instead.\n"
            "Make the contrast clear and emotional. Give one concrete example. End with one simple action. "
            + ("This is the last item, so do not tease a next one." if last else
               "Then end with one short curiosity line that teases the next item without naming it."),
            max(60, item_w // 2), int(item_w * 2.4), so_far=" ".join(parts))
        if txt:
            if not txt.lower().startswith(lab.lower()[:-1]): txt = f"{lab} {txt}"
            parts.append(txt)
        if i == n // 2: parts.append(CTA_MID)
    final = _chunk(
        f"Video title: {job['title']}\nWrite the FINAL section (about {outro_w} words).\n"
        "Recap the whole list in one or two short sentences. Give one simple action the viewer can start today.\n"
        f"Finish with one calm closing line. Then say exactly this: \"{CTA_END}\"",
        80, 540, so_far=" ".join(parts))
    if final: parts.append(final)
    text = " ".join(parts)
    if wc(text) < spec["words_hard_min"]: raise RuntimeError(f"Long script too short ({wc(text)} words)")
    print(f"[script] long: {wc(text)} words, {n} items")
    return text

def write_short(job, outline=None):
    spec, n = SPECS["short"], job["n"]
    lo, hi = spec["words_target"]; alo, ahi = spec["words_accept"]
    labs = labels(job); items = outline or _outline(job)
    plan = "\n".join(f"{lab} {it}" for lab, it in zip(labs, items))
    pat = re.compile(r"\b" + job["label"] + r"\s+(" + "|".join(NUMW[1:]) + r")\b", re.I)
    last = None
    for attempt in range(3):
        strict = "" if attempt == 0 else f" STRICT: between {lo} and {hi} words."
        prompt = (f"Video title: {job['title']}\nWrite a YouTube Short of about {(lo + hi) // 2} words.\n"
                  f"Open with a curiosity hook. Present these items in order, each starting with its label.\n"
                  f"For each item: FIRST what the poor do, THEN what the rich do.\n"
                  f"At the end, ask them to subscribe and comment which country they are watching from.{strict}\n{plan}\n"
                  "Output ONLY the spoken narration.")
        try:
            raw = ask(prompt, system=SYSTEM, max_tokens=900,
                      validate=lambda t: alo <= wc(_clean(t)) <= ahi and not _bad_opener(_clean(t)))
        except RuntimeError: time.sleep(20); continue
        last = _clean(raw)
        if alo <= wc(last) <= ahi and len(pat.findall(last)) >= n: break
    if not last: raise RuntimeError("Could not write the short script")
    print(f"[script] short: {wc(last)} words, {len(pat.findall(last))}/{n} labels")
    return last

def write(job, outline=None):
    return write_long(job, outline) if job["kind"] == "long" else write_short(job, outline)

def get_outline(job):
    return _outline(job)

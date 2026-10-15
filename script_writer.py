"""Hook + curiosity script writer. Long scripts are written in chunks so free models can keep up."""
import re
import time

from llm import ask
from config import SPECS

SYSTEM = (
    "You are a scriptwriter for a calm, wise finance YouTube channel for viewers in the USA, UK, Canada and Australia.\n"
    "Output ONLY the words the narrator speaks. No titles, no labels, no brackets, no markdown, no timestamps, "
    "no stage directions, no emojis.\n"
    "Tone: calm, slow, confident, wise, like a mentor talking to a young person. Short clear sentences. Plain English.\n"
    "Be factual. Never promise guaranteed profits or returns. Never tell the viewer to buy a specific stock or coin.\n"
    "Never start with: Hello, Welcome, In this video, Have you ever."
)
FORBIDDEN = ("hello", "welcome", "in this video", "have you ever", "hi ", "hey ")
LABEL = re.compile(r"^\s*(voice|narrator|host|title|scene\s*\d*|part\s*\d*|intro|outro|hook|script|section\s*\d*)\s*[:\-–].*$", re.I)
BARE = re.compile(r"^\s*#*\s*(part|scene|section|chapter)\s*\d+\s*$", re.I)
PREAMBLE = re.compile(r"^\s*(sure|certainly|here is|here's|okay|of course)\b.*:\s*$", re.I)


def clean(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?", " ", text)
    lines = []
    for ln in text.splitlines():
        ln = re.sub(r"[*_`]", "", ln).lstrip("# ")
        if LABEL.match(ln) or BARE.match(ln) or PREAMBLE.match(ln):
            continue
        ln = re.sub(r"^\s*#+\s*", "", ln)
        ln = re.sub(r"^\s*[-*•]\s+", "", ln)
        lines.append(ln)
    text = " ".join(lines)
    text = re.sub(r"[*_#`>~|]", "", text)
    text = text.replace("—", ", ").replace("–", ", ")
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r",\s*,+", ",", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().strip('"')


def wc(text):
    return len(text.split())


def _bad_opener(text):
    return text.lower().lstrip().startswith(FORBIDDEN)


def _tail(text, n=120):
    return " ".join(text.split()[-n:])


def _chunk(topic, instruction, so_far="", lo=250, hi=800, hook=False):
    ctx = ""
    if so_far:
        ctx = (f'The narration so far ends with: "{_tail(so_far)}"\n'
               "Continue smoothly from there. Do not repeat anything already said and do not restart.\n")
    prompt = f"Topic (a real YouTube search phrase): {topic}\n\n{instruction}\n\n{ctx}Output ONLY the spoken narration."

    def ok(raw):
        c = clean(raw)
        return lo <= wc(c) <= hi and not (hook and _bad_opener(c))

    def ok_loose(raw):
        c = clean(raw)
        return max(120, lo // 2) <= wc(c) <= hi * 2 and not (hook and _bad_opener(c))

    for attempt in range(3):
        try:
            return clean(ask(prompt, system=SYSTEM, max_tokens=1800, validate=ok if attempt == 0 else ok_loose))
        except RuntimeError:
            print(f"[script] chunk failed (attempt {attempt + 1}), waiting before retry")
            time.sleep(20)
    return None


def _outline(topic, n=8):
    prompt = (f"Topic: {topic}\nList {n} distinct, specific, practical points for a finance video on this topic. "
              "One short line each, numbered 1 to " + str(n) + ". Output only the numbered list.")
    try:
        raw = ask(prompt, max_tokens=500, validate=lambda t: len(re.findall(r"^\s*\d+[.)]", t, re.M)) >= 4)
        pts = [m.group(1).strip() for m in re.finditer(r"^\s*\d+[.)]\s*(.+)$", raw, re.M)]
        if len(pts) >= 4:
            return pts
    except Exception:
        pass
    return [f"the first big idea behind {topic}", "the mistake most people make", "the habit that changes everything",
            "the numbers that surprise people", "the simple system that works", "the trap to avoid",
            "the long-term view", "the first step to take this week"]


def write_long(topic):
    spec = SPECS["long"]
    points = _outline(topic)
    opening = _chunk(
        topic,
        "Write the OPENING of the video (about 380 words). Start with a shocking, curiosity-driven hook in the first "
        "one or two sentences. Then build up why this matters. End by teasing the first point as a question you have "
        "not answered yet.", lo=250, hook=True)
    if not opening:
        raise RuntimeError("Could not write the opening of the long script")
    parts = [opening]
    used_pts = 0
    while used_pts < len(points):
        total = sum(wc(p) for p in parts)
        if used_pts >= 4 and total + 400 >= spec["words_target_total"]:
            break
        pt = points[used_pts]
        sec = _chunk(
            topic,
            f"Write the NEXT section (about 420 words) covering this point: {pt}. Open by answering the question teased "
            "before. Give a concrete example with numbers or a short story. Near the middle, tease a question about the "
            "next part before answering it. Do NOT conclude the video.",
            so_far=" ".join(parts))
        if sec:
            parts.append(sec)
        used_pts += 1
    final = _chunk(
        topic,
        "Write the FINAL section (about 400 words): pull the points together, deliver the big payoff promised in the "
        "hook, and end with one calm, memorable closing line. Do not say subscribe or like.",
        so_far=" ".join(parts))
    if final:
        parts.append(final)
    text = " ".join(parts)
    if wc(text) < spec["words_hard_min"]:
        raise RuntimeError(f"Long script too short ({wc(text)} words)")
    print(f"[script] long: {wc(text)} words")
    return text


def write_short(topic):
    spec = SPECS["short"]
    lo, hi = spec["words_target"]
    alo, ahi = spec["words_accept"]
    last = None
    for attempt in range(3):
        strict = "" if attempt == 0 else f" STRICT: it must be between {lo} and {hi} words, count carefully."
        prompt = (f"Topic (a real YouTube search phrase): {topic}\n\nWrite a YouTube Short narration of about "
                  f"{(lo + hi) // 2} words. Hook in the first sentence, one curiosity question in the middle, "
                  f"a clear payoff at the end.{strict} Output ONLY the spoken narration.")
        try:
            raw = ask(prompt, system=SYSTEM, max_tokens=900,
                      validate=lambda t: alo <= wc(clean(t)) <= ahi and not _bad_opener(clean(t)))
        except RuntimeError:
            time.sleep(20)
            continue
        last = clean(raw)
        if alo <= wc(last) <= ahi:
            break
    if not last:
        raise RuntimeError("Could not write the short script")
    print(f"[script] short: {wc(last)} words")
    return last


def write(kind, topic):
    return write_long(topic) if kind == "long" else write_short(topic)

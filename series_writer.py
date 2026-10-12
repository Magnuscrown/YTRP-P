"""
STEP 1: LLM fallback router + series writer
Run:  python series_writer.py "hidden boss everyone looks down on" 10
Needs: pip install requests
Set API keys as environment variables (GitHub Secrets later):
  GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY, CEREBRAS_API_KEY
Models are picked automatically from each provider's live model list.
"""
import os, sys, json, re, time, requests

# (name, base url, key env var, optional model override env var, preferred keywords in order)
# Model names change all the time, so we ask each provider for its CURRENT model list
# and pick the best match automatically. To force a model, set e.g. GROQ_MODEL as a secret.
PROVIDERS = [
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY",
     "GEMINI_MODEL", ["flash", "pro"]),
    ("groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY",
     "GROQ_MODEL", ["gpt-oss-120b", "llama-3.3-70b", "llama-4", "qwen", "llama"]),
    ("cerebras", "https://api.cerebras.ai/v1", "CEREBRAS_API_KEY",
     "CEREBRAS_MODEL", ["gpt-oss", "llama", "qwen"]),
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
     "OPENROUTER_MODEL", ["gpt-oss", "llama-3.3", "deepseek", "qwen", "gemma", "llama"]),
    ("nvidia", "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
     "NVIDIA_MODEL", ["llama-3.3-70b", "llama-3.1-70b", "nemotron", "llama"]),
]
# words that mean "not a normal chat model"
SKIP = ("whisper", "guard", "tts", "embed", "vision", "image", "audio", "orpheus", "safeguard",
        "rerank", "moderation", "transcribe", "playai", "imagen", "veo", "lyria", "aqa",
        "reward", "parse", "clip", "-vl", "ocr", "translate", "safety")
_cache = {}


def candidates(name, base, key, override_env, prefs):
    """Return up to 4 chat models to try for this provider, best first."""
    if os.getenv(override_env):
        return [os.getenv(override_env)]
    if name in _cache:
        return _cache[name]
    ids = []
    try:
        r = requests.get(base + "/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
        r.raise_for_status()
        ids = [m["id"].replace("models/", "") for m in r.json().get("data", [])]
    except Exception as e:
        print(f"[warn] {name}: could not list models: {e}")
    ids = [i for i in ids if not any(w in i.lower() for w in SKIP)]
    if name == "openrouter":
        ids = [i for i in ids if i.endswith(":free")]

    def rank(i):
        low = i.lower()
        k = next((n for n, p in enumerate(prefs) if p in low), len(prefs))
        unstable = any(w in low for w in ("preview", "exp", "latest", "thinking"))
        m = re.search(r"(\d+(?:\.\d+)?)", low)
        version = float(m.group(1)) if m else 0.0
        return (k, unstable, "lite" in low, -version, len(i))     # best keyword match, then newest version

    ids.sort(key=rank)
    _cache[name] = ids[:4]
    print(f"[info] {name} models to try: {_cache[name]}")
    return _cache[name]


_cool = {}      # provider -> time when it may be tried again (after a rate limit or overload)


def ask(prompt, system="You are a helpful assistant.", temperature=0.9):
    """Try each provider (and its best models). A provider that says "rate limit" is rested for a while,
    and if EVERY provider is busy we wait and try again instead of crashing."""
    errors = []
    for attempt in range(5):
        tried = False
        for name, base, key_env, override_env, prefs in PROVIDERS:
            key = os.getenv(key_env)
            if not key or _cool.get(name, 0) > time.time():
                continue
            tried = True
            for model in candidates(name, base, key, override_env, prefs):
                try:
                    r = requests.post(
                        base + "/chat/completions",
                        headers={"Authorization": f"Bearer {key}"},
                        json={"model": model, "temperature": temperature,
                              "messages": [{"role": "system", "content": system},
                                           {"role": "user", "content": prompt}]},
                        timeout=120,
                    )
                    if r.status_code != 200:
                        msg = f"{name}/{model}: {r.status_code} {r.text[:150]}"
                        print("[fail]", msg)
                        errors.append(msg)
                        if r.status_code == 429:
                            _cool[name] = time.time() + 90      # rate limit / quota: rest this provider
                            break
                        if r.status_code in (401, 403):
                            _cool[name] = time.time() + 3600    # bad key: do not retry this run
                            break
                        if r.status_code in (500, 502, 503, 504):
                            _cool[name] = time.time() + 30
                        continue
                    text = r.json()["choices"][0]["message"]["content"]
                    print(f"[ok] answered by {name}/{model}")
                    return text
                except Exception as e:
                    msg = f"{name}/{model}: {str(e)[:120]}"
                    print("[fail]", msg)
                    errors.append(msg)
                    if "timed out" in str(e):
                        _cool[name] = time.time() + 30
                        break
        waits = [t - time.time() for n, t in _cool.items() if t > time.time()]
        wait = min(max(5, min(waits) if waits else 20), 60)
        print(f"[wait] all providers busy or limited, waiting {wait:.0f}s (round {attempt + 1}/5)")
        time.sleep(wait)
    raise RuntimeError("All providers failed -> " + " | ".join(errors[-6:]))


def parse_json(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    chunk = text[start:end + 1]
    try:
        return json.loads(chunk)
    except json.JSONDecodeError:
        try:                                    # the AI sometimes forgets a comma or quote: repair it
            from json_repair import repair_json
            return json.loads(repair_json(chunk))
        except ImportError:
            raise


def ask_json(prompt, system="You write original, emotional short-form story series. Reply with JSON only."):
    for attempt in range(3):
        try:
            return parse_json(ask(prompt, system, temperature=0.6))
        except Exception as e:
            print(f"[retry] bad JSON ({str(e)[:120]})")
    raise RuntimeError("Could not get valid JSON")


BURSTS = int(os.getenv("BURSTS") or 4)            # action beats per part
BURST_FRAMES = int(os.getenv("BURST_FRAMES") or 4)  # quick pictures per action beat


def write_series(theme, parts=10):
    # STEP A: plan the WHOLE story first (beginning to end) so every part fits together
    outline = ask_json(f"""Plan an ORIGINAL {parts}-part story for vertical videos.
Theme inspiration (do not copy any existing story): {theme}

Return JSON exactly like this:
{{
  "title": "...",
  "logline": "one sentence: who, what they want, what is hidden, what is at stake",
  "characters": [{{"name": "...", "look": "very detailed visual description (age, hair, clothes, colors)"}}],
  "style": "one line describing the art style used in EVERY image (e.g. 3D Pixar-style cartoon, cinematic lighting)",
  "beats": ["Part 1: ...", "Part 2: ...", "... one line per part, {parts} total ..."]
}}
Rules: Part 1 is the true beginning (introduce the main character, the world, the hidden secret).
The beats must build step by step with rising tension and reach a big twist and a satisfying ending in part {parts}.""")

    chars = "; ".join(f"{c['name']} ({c['look']})" for c in outline["characters"])
    beats = "\n".join(outline["beats"])
    result = {"title": outline["title"], "logline": outline.get("logline", ""),
              "characters": outline["characters"], "style": outline["style"], "parts": []}
    previous = ""

    # STEP B: write each part, knowing the whole plan and how the last part ended
    for n in range(1, parts + 1):
        role = ("This is the VERY FIRST part: open with a gripping hook line, then introduce the main "
                "character and the world from the beginning. Do not start in the middle." if n == 1 else
                "This is the FINAL part: deliver the big reveal and a satisfying ending." if n == parts else
                "Continue directly from where the previous part ended.")
        part = ask_json(f"""Write part {n} of {parts} of this story.
TITLE: {outline['title']}
LOGLINE: {outline.get('logline', '')}
CHARACTERS: {chars}
FULL PLAN:
{beats}

PREVIOUS PART ENDED WITH: {previous or '(nothing, this is the start)'}

{role}
Rules:
- Tell the part as exactly 12 BEATS in order. Each beat has "line" (the spoken narration for that moment, 10-16 words) and "image" (ONE picture prompt showing exactly what the line says, with camera angle, naming the characters, no text in the image).
- Total narration about 140-170 words (about 60 seconds). Spoken storytelling in simple, vivid English: real scenes, action and short dialogue lines. Not a summary.
- Exactly {BURSTS} of the 12 beats are ACTION beats (someone falls, raises a hand, slams a door, runs, gets pushed, gasps, everyone turns). For those, replace "image" with "burst": a list of exactly {BURST_FRAMES} prompts showing the SAME action in {BURST_FRAMES} quick stages (start to end), and keep that beat's "line" short (max 8 words). Spread the action beats across the whole part, not all together.
- Parts 1 to {parts - 1} end on a cliffhanger.

Return JSON: {{"title": "short part title", "beats": [{{"line": "...", "image": "..."}}, {{"line": "...", "burst": ["..." x {BURST_FRAMES}]}}]}}""")
        part["part"] = n
        part["narration"] = " ".join(b_["line"] for b_ in part["beats"])
        result["parts"].append(part)
        previous = " ".join(part["narration"].split()[-40:])
        print(f"[ok] wrote part {n}/{parts}")
    return result


if __name__ == "__main__":
    default_theme = "a quiet new student is secretly the owner of the school"
    theme = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else default_theme
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() else 10
    series = write_series(theme, n)
    os.makedirs("out", exist_ok=True)
    with open("out/series.json", "w") as f:
        json.dump(series, f, indent=2, ensure_ascii=False)
    print(f"Saved out/series.json: {series['title']} ({len(series['parts'])} parts)")

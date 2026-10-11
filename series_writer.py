"""
STEP 1: LLM fallback router + series writer
Run:  python series_writer.py "hidden boss everyone looks down on" 10
Needs: pip install requests
Set API keys as environment variables (GitHub Secrets later):
  GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY, CEREBRAS_API_KEY
Models are picked automatically from each provider's live model list.
"""
import os, sys, json, re, requests

# (name, base url, key env var, optional model override env var, preferred keywords in order)
# Model names change all the time, so we ask each provider for its CURRENT model list
# and pick the best match automatically. To force a model, set e.g. GROQ_MODEL as a secret.
PROVIDERS = [
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY",
     "GEMINI_MODEL", ["2.5-flash", "flash", "pro"]),
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
        return (k, unstable, len(i))

    ids.sort(key=rank)
    _cache[name] = ids[:4]
    print(f"[info] {name} models to try: {_cache[name]}")
    return _cache[name]


def ask(prompt, system="You are a helpful assistant."):
    """Try each provider (and its best models) in order. Failure or rate limit -> next one."""
    errors = []
    for name, base, key_env, override_env, prefs in PROVIDERS:
        key = os.getenv(key_env)
        if not key:
            continue
        for model in candidates(name, base, key, override_env, prefs):
            try:
                r = requests.post(
                    base + "/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.9,
                    },
                    timeout=120,
                )
                if r.status_code != 200:
                    msg = f"{name}/{model}: {r.status_code} {r.text[:200]}"
                    print("[fail]", msg)
                    errors.append(msg)
                    if r.status_code in (401, 403, 429):
                        break  # bad key or rate limit: skip the rest of this provider
                    continue
                text = r.json()["choices"][0]["message"]["content"]
                print(f"[ok] answered by {name}/{model}")
                return text
            except Exception as e:
                msg = f"{name}/{model}: {e}"
                print("[fail]", msg)
                errors.append(msg)
    raise RuntimeError("All providers failed -> " + " | ".join(errors))


def parse_json(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def write_series(theme, parts=10):
    system = "You write original, emotional short-form story series. Reply with JSON only."
    prompt = f"""Create an ORIGINAL {parts}-part story series for vertical videos.
Theme inspiration (do not copy any existing story): {theme}

Rules:
- Each part is about 130-160 words of narration (about 60 seconds).
- Every part ends on a cliffhanger, except the last which gives a satisfying twist.
- Keep characters consistent. Define them once in "characters".
- Each part has 6 image prompts describing scenes in a consistent cartoon/3D avatar style.

Return JSON in exactly this shape:
{{
  "title": "...",
  "characters": [{{"name": "...", "look": "detailed visual description"}}],
  "style": "one line describing the art style used in every image",
  "parts": [
    {{"part": 1, "title": "...", "narration": "...", "image_prompts": ["...", "..."]}}
  ]
}}"""
    for attempt in range(2):
        try:
            return parse_json(ask(prompt, system))
        except Exception as e:
            print(f"[retry] bad JSON ({e})")
    raise RuntimeError("Could not get valid JSON")


if __name__ == "__main__":
    default_theme = "a quiet new student is secretly the owner of the school"
    theme = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else default_theme
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() else 10
    series = write_series(theme, n)
    os.makedirs("out", exist_ok=True)
    with open("out/series.json", "w") as f:
        json.dump(series, f, indent=2, ensure_ascii=False)
    print(f"Saved out/series.json: {series['title']} ({len(series['parts'])} parts)")

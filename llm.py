"""AI text with 3 free providers, paced and with live model discovery (never hardcodes a model name).
Order: OpenRouter free models -> Groq (live list) -> Cloudflare Workers AI (live list).
Uses only `requests`. Secrets are read from env: OPENROUTER_API_KEY, GROQ_API_KEY, CF_ACCOUNT_ID, CF_API_TOKEN."""
import os
import random
import re
import time

import requests

OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
CF_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_TOKEN = os.getenv("CF_API_TOKEN", "")

MIN_GAP = {"openrouter": 3.5, "groq": 2.5, "cloudflare": 0.5}   # seconds between calls (keeps under per-minute limits)
MAX_MODELS_PER_CALL = {"openrouter": 6, "groq": 5, "cloudflare": 4}

_models = {}
_dead = set()
_cool = {}
_last = {}


# ------------------------------------------------------------------ helpers
def _strip(text):
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I).strip()


def _pace(p):
    gap = MIN_GAP[p] - (time.time() - _last.get(p, 0))
    if gap > 0:
        time.sleep(gap)
    _last[p] = time.time()


def _cooling(p):
    return time.time() < _cool.get(p, 0)


def _extract(data):
    """Reads the answer from OpenAI-style and Cloudflare-style responses."""
    if not isinstance(data, dict):
        return ""
    if data.get("choices"):
        return (data["choices"][0].get("message") or {}).get("content") or ""
    res = data.get("result")
    if isinstance(res, dict):
        if res.get("response"):
            return res["response"] if isinstance(res["response"], str) else ""
        if res.get("choices"):
            return (res["choices"][0].get("message") or {}).get("content") or ""
    return ""


def _msgs(prompt, system):
    m = [{"role": "system", "content": system}] if system else []
    return m + [{"role": "user", "content": prompt}]


# ------------------------------------------------------------------ model discovery
def _discover(p):
    if p in _models:
        return _models[p]
    out = []
    try:
        if p == "openrouter":
            r = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
            for m in r.json().get("data", []):
                pr = m.get("pricing") or {}
                mod = (m.get("architecture") or {}).get("modality", "text->text")
                if (str(pr.get("prompt")) == "0" and str(pr.get("completion")) == "0" and mod.endswith("->text")
                        and "embed" not in m["id"].lower() and (m.get("context_length") or 0) >= 8000
                        and "safety" not in m["id"].lower()):
                    out.append(m["id"])
            random.shuffle(out)
        elif p == "groq":
            r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {GROQ_KEY}"}, timeout=30)
            ids = [m["id"] for m in r.json().get("data", []) if m.get("active", True)]
            ids = [i for i in ids if not re.search(r"whisper|guard|tts|orpheus|playai|embed|safeguard", i, re.I)]
            score = lambda i: (0 if re.search(r"70b|120b|versatile|qwen|scout|maverick|kimi", i, re.I) else 1, i)
            out = sorted(ids, key=score)
        elif p == "cloudflare":
            r = requests.get(f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/models/search",
                             params={"task": "Text Generation", "per_page": 100},
                             headers={"Authorization": f"Bearer {CF_TOKEN}"}, timeout=30)
            names = [m.get("name", "") for m in r.json().get("result", [])]
            names = [n for n in names if n.startswith("@cf/") and not re.search(r"coder|guard|vision|embed|sql|safety|reasoning-distill", n, re.I)]
            prefs = ["llama-3.3-70b", "llama-4", "llama-3.1-70b", "qwen", "llama-3.1-8b", "mistral", "gemma", "llama-3"]
            rank = lambda n: next((i for i, k in enumerate(prefs) if k in n), len(prefs))
            out = sorted(names, key=rank)
    except Exception as e:
        print(f"[llm] {p}: could not list models ({type(e).__name__})")
    _models[p] = out
    print(f"[llm] {p}: {len(out)} models found")
    return out


# ------------------------------------------------------------------ one call
def _call(p, model, prompt, system, max_tokens, temperature):
    """Returns (status_code, text, error_text, retry_after_seconds)."""
    msgs = _msgs(prompt, system)
    if p == "openrouter":
        url, headers = "https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {OR_KEY}"}
        body = {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature}
    elif p == "groq":
        url, headers = "https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {GROQ_KEY}"}
        body = {"model": model, "messages": msgs, "max_tokens": min(max_tokens, 6000), "temperature": temperature}
    else:
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/{model}"
        headers = {"Authorization": f"Bearer {CF_TOKEN}"}
        body = {"messages": msgs, "max_tokens": max_tokens, "temperature": temperature}
    try:
        r = requests.post(url, headers=headers, json=body, timeout=150)
    except Exception as e:
        return 0, "", type(e).__name__, 0
    ra = 0
    try:
        ra = float(r.headers.get("retry-after", 0))
    except Exception:
        pass
    if r.status_code == 200:
        try:
            return 200, _strip(_extract(r.json())), "", 0
        except Exception:
            return 200, "", "bad json", 0
    return r.status_code, "", r.text[:300], ra


def _run_provider(p, prompt, system, max_tokens, temperature, validate):
    key = {"openrouter": OR_KEY, "groq": GROQ_KEY, "cloudflare": CF_TOKEN and CF_ID}[p]
    if not key or _cooling(p):
        return None
    tried, limited = 0, 0
    for model in _discover(p):
        if model in _dead:
            continue
        if tried >= MAX_MODELS_PER_CALL[p] or limited >= 2:
            break
        tried += 1
        for attempt in range(2):
            _pace(p)
            status, text, err, ra = _call(p, model, prompt, system, max_tokens, temperature)
            if status == 200 and text:
                if validate is None or validate(text):
                    return text
                print(f"[llm] {p}/{model}: answer rejected")
                break
            if status == 429 or (status == 200 and not text and "rate" in err.lower()):
                low = err.lower()
                if any(k in low for k in ("per-day", "per day", "daily", "neurons", "quota")):
                    _cool[p] = time.time() + 6 * 3600
                    print(f"[llm] {p}: daily limit reached, skipping it for this run")
                    return None
                limited += 1 if attempt == 1 else 0
                wait = min(max(ra, 12 * (attempt + 1)), 40)
                print(f"[llm] {p}/{model}: rate limited, waiting {wait:.0f}s")
                time.sleep(wait)
                continue
            if status in (400, 401, 403, 404, 410, 422):
                print(f"[llm] {p}/{model}: HTTP {status}")
                if status in (401, 403) and p != "openrouter":
                    _cool[p] = time.time() + 6 * 3600
                    return None
                _dead.add(model)
                break
            print(f"[llm] {p}/{model}: HTTP {status or 'error'} {err[:60]}")
            break
    if limited >= 2:
        _cool[p] = time.time() + 90
    return None


def ask(prompt, system="", max_tokens=2000, validate=None, temperature=0.8, max_tries=None):
    for p in ("openrouter", "groq", "cloudflare"):
        text = _run_provider(p, prompt, system, max_tokens, temperature, validate)
        if text:
            return text
    raise RuntimeError("All AI providers failed for this request")

"""Free-model discovery + fallback chain. Never hardcodes a model name."""
import random
import re
import time

import requests
import litellm

from config import OPENROUTER_API_KEY, GROQ_API_KEY

litellm.suppress_debug_info = True
GROQ_FALLBACK = "groq/llama-3.1-8b-instant"

_models_cache = None
_dead = set()   # models that returned 404/400 this run


def free_models():
    """Live list of free OpenRouter text models (fetched once per run)."""
    global _models_cache
    if _models_cache is not None:
        return _models_cache
    found = []
    try:
        r = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
        r.raise_for_status()
        for m in r.json().get("data", []):
            p = m.get("pricing") or {}
            if str(p.get("prompt")) != "0" or str(p.get("completion")) != "0":
                continue
            mod = (m.get("architecture") or {}).get("modality", "text->text")
            if not mod.endswith("->text") or "embed" in m["id"].lower():
                continue
            if (m.get("context_length") or 0) < 8000:
                continue
            found.append(m["id"])
        random.shuffle(found)
    except Exception as e:
        print(f"[llm] could not fetch OpenRouter model list: {e}")
    _models_cache = found
    print(f"[llm] {len(found)} free OpenRouter models discovered")
    return found


def _strip(text):
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    return text.strip()


def _call(model, key, prompt, system, max_tokens, temperature):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    resp = litellm.completion(
        model=model, messages=msgs, api_key=key,
        max_tokens=max_tokens, temperature=temperature, timeout=120,
    )
    return _strip(resp.choices[0].message.content)


def ask(prompt, system="", max_tokens=2000, validate=None, temperature=0.8, max_tries=25):
    """Try every free OpenRouter model until one gives a valid answer, then Groq."""
    tries = 0
    if OPENROUTER_API_KEY:
        for mid in free_models():
            if mid in _dead:
                continue
            if tries >= max_tries:
                break
            tries += 1
            try:
                text = _call(f"openrouter/{mid}", OPENROUTER_API_KEY, prompt, system, max_tokens, temperature)
                if text and (validate is None or validate(text)):
                    return text
                print(f"[llm] {mid}: answer rejected")
            except Exception as e:
                name = type(e).__name__
                if "NotFound" in name or "BadRequest" in name:
                    _dead.add(mid)
                print(f"[llm] {mid}: {name}")
                time.sleep(1)
    if GROQ_API_KEY:
        for _ in range(2):
            try:
                text = _call(GROQ_FALLBACK, GROQ_API_KEY, prompt, system, min(max_tokens, 6000), temperature)
                if text and (validate is None or validate(text)):
                    return text
                print("[llm] groq: answer rejected")
            except Exception as e:
                print(f"[llm] groq: {type(e).__name__}")
                time.sleep(2)
    raise RuntimeError("All AI models failed for this request")

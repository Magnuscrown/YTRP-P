"""
STEP 1: LLM fallback router + series writer
Run:  python series_writer.py "hidden boss everyone looks down on" 10
Needs: pip install requests
Set API keys as environment variables (GitHub Secrets later):
  GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY, CEREBRAS_API_KEY
NOTE: free model names change often. If one provider keeps failing,
check its docs for the current free model name and edit PROVIDERS below.
"""
import os, sys, json, re, requests

# (name, url, env var for key, model) - all OpenAI-compatible
PROVIDERS = [
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
     "GEMINI_API_KEY", "gemini-2.5-flash"),
    ("groq", "https://api.groq.com/openai/v1/chat/completions",
     "GROQ_API_KEY", "llama-3.3-70b-versatile"),
    ("cerebras", "https://api.cerebras.ai/v1/chat/completions",
     "CEREBRAS_API_KEY", "llama-3.3-70b"),
    ("openrouter", "https://openrouter.ai/api/v1/chat/completions",
     "OPENROUTER_API_KEY", "meta-llama/llama-3.3-70b-instruct:free"),
    ("nvidia", "https://integrate.api.nvidia.com/v1/chat/completions",
     "NVIDIA_API_KEY", "meta/llama-3.1-70b-instruct"),
]


def ask(prompt, system="You are a helpful assistant."):
    """Try each provider in order. If one fails or hits its limit, go to the next."""
    errors = []
    for name, url, key_env, model in PROVIDERS:
        key = os.getenv(key_env)
        if not key:
            continue
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.9,
                },
                timeout=90,
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
            print(f"[ok] answered by {name}")
            return text
        except Exception as e:
            print(f"[fail] {name}: {e}")
            errors.append(f"{name}: {e}")
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
    theme = sys.argv[1] if len(sys.argv) > 1 else "a quiet new student is secretly the owner of the school"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    series = write_series(theme, n)
    os.makedirs("out", exist_ok=True)
    with open("out/series.json", "w") as f:
        json.dump(series, f, indent=2, ensure_ascii=False)
    print(f"Saved out/series.json: {series['title']} ({len(series['parts'])} parts)")

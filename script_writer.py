import os
import re
import requests
from litellm import completion
from config import OPENROUTER_API_KEY, GROQ_API_KEY

os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY or ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""


def get_current_free_openrouter_models():
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        )
        response.raise_for_status()
        models = response.json().get("data", [])
        return [m["id"] for m in models if m.get("pricing", {}).get("prompt") == "0"]
    except Exception as e:
        print(f"⚠️ Could not fetch models: {repr(e)}")
        return []


def build_prompt(topic, video_type):
    if video_type == "long":
        length = "10 minutes (about 1500 words)"
    else:
        length = "45 seconds (about 120 words)"

    return f"""You are a viral YouTube script writer for a MOTIVATIONAL FINANCE channel.

Write a {length} narration script about: {topic}

ABSOLUTE RULES:
1. Output ONLY narration text — no titles, no labels, no brackets, no markdown.
2. Start with a shocking hook in the first 1-2 sentences. No "Hello", "Welcome", "Have you ever".
3. Open a new curiosity loop every 20-30 seconds. Tease answers before revealing them.
4. Every word will be spoken aloud. Nothing for the eyes only.
5. Tone: calm, slow, confident, wise — like a mentor explaining to a young person.
6. Simple words only. Short sentences. Slow rhythm.
7. End with a soft insight and a subtle push to subscribe.

STRUCTURE:
- Hook: shocking truth or counterintuitive statement
- Build-up: why this matters
- Body: 3-5 powerful points, each with a mini-reveal
- Payoff: surprising final insight

LENGTH: exactly {length}.

Output ONLY the narration. Begin now."""


def write_script(topic, video_type="long"):
    print(f"✍️ Writing script: {topic}")
    prompt = build_prompt(topic, video_type)

    free_models = get_current_free_openrouter_models()
    fallback_models = [f"openrouter/{m}" for m in free_models]
    fallback_models.append("groq/llama-3.1-8b-instant")

    for model_name in fallback_models:
        try:
            print(f"🔄 Trying {model_name}...")
            response = completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_tokens=4000,
            )
            script = response.choices[0].message.content.strip()

            # Clean
            script = script.replace("**", "").replace("##", "")
            script = re.sub(r'\[.*?\]', '', script)
            script = re.sub(r'\(.*?\)', '', script)
            script = re.sub(r'\s+', ' ', script)

            print(f"✅ Script by {model_name}")
            return script.strip()
        except Exception as e:
            print(f"⚠️ {model_name} failed: {repr(e)[:150]}")
            continue

    print("❌ All models failed.")
    return f"Script generation failed for: {topic}"

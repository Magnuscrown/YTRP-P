import os
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
        free_models = [
            m["id"] for m in models
            if m.get("pricing", {}).get("prompt") == "0"
        ]
        print(f"🔍 Found {len(free_models)} free models on OpenRouter")
        return free_models
    except Exception as e:
        print(f"⚠️ Could not fetch OpenRouter models: {repr(e)}")
        return []


def build_prompt(topic, video_type):
    if video_type == "long":
        length = "10 minutes (about 1500 words)"
    else:
        length = "45 seconds (about 120 words)"

    return f"""You are a viral YouTube script writer. Write ONLY the narration for a {length} video about: {topic}.

ABSOLUTE RULES — you MUST follow every one:
1. Output ONLY the words the narrator speaks. Nothing else.
2. NO titles, NO headings, NO labels like "Voice:" or "Narrator:".
3. NO square brackets, NO scene directions, NO visual descriptions.
4. NO markdown (no #, no *, no -, no bold, no italics).
5. NO timestamps, NO scene numbers, NO section headers.
6. Every word you write will be spoken aloud. Nothing is for the eyes only.

THE HOOK (first 1-2 sentences — THIS IS THE MOST IMPORTANT PART):
- Start with a shocking, curiosity-inducing statement or question.
- Make the viewer feel like they MUST keep watching to find out the answer.
- Never start with "Hello", "Welcome", "In this video", or "Have you ever".
- Use patterns like:
  * "Most people believe X — but the truth is the opposite."
  * "There is a reason [strange thing] happens, and once you know it, you cannot un-know it."
  * "If you do this one thing, [surprising consequence] — and almost nobody knows why."
- The hook must create a GAP in the viewer's mind that only the rest of the video can close.

CURIOSITY THROUGHOUT (every 20-30 seconds):
- Open a new "loop" — say something intriguing, but don't reveal it yet.
- Example: "But here is the part that really surprised me..." → pause → reveal.
- Example: "And what I found next changes everything."
- Never answer a question immediately. Always tease the answer first.
- Use short sentences. Short paragraphs. Slow rhythm.

STRUCTURE:
- Hook (5-15 seconds): the shocking opening.
- Build-up (30-60 seconds): explain why this matters. Add a second curiosity loop.
- Body (rest of the video): 3-5 key points, each ending with a mini-reveal that pushes to the next.
- Payoff (last 15 seconds): deliver the final surprising insight. End with a soft open loop into the next video idea.

TONE:
- Calm, slow, confident, curious — like a wise friend explaining a secret to a 5-year-old.
- Simple words only. No jargon. No complexity.
- Every sentence should feel like the next piece of a puzzle.

LENGTH: exactly {length}.

OUTPUT: Only the narration text. Begin with the hook. Nothing before it. Nothing after it. Start now."""


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
                temperature=0.85,  # Higher = more creative hooks
                max_tokens=4000,
            )
            script = response.choices[0].message.content.strip()

            # Clean up any accidental formatting
            script = script.replace("**", "").replace("##", "")
            script = script.replace("Voice:", "").replace("Narrator:", "")
            script = script.replace("Host:", "")

            # Remove label/header-looking lines
            cleaned_lines = []
            for line in script.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.endswith(":") and len(stripped) < 40:
                    continue
                if stripped.startswith(("#", "*", "-", "[", "Scene")):
                    continue
                cleaned_lines.append(stripped)

            script = " ".join(cleaned_lines)

            print(f"✅ Script written by {model_name}")
            return script
        except Exception as e:
            print(f"⚠️ {model_name} failed: {repr(e)}")
            continue

    print("❌ All AI providers failed.")
    return f"Script generation failed for topic: {topic}"

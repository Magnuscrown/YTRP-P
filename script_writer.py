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
        length = "10 minutes"
    else:
        length = "45 seconds"
    
    return f"""You are a YouTube script writer. Write ONLY the narration text for a {length} video about: {topic}.

STRICT RULES — you MUST follow every single one:
1. Output ONLY the words the narrator will speak. Nothing else.
2. Do NOT write any title, heading, or label.
3. Do NOT write "Voice:", "Narrator:", "Host:", or any speaker name.
4. Do NOT write anything in square brackets like [Character smiles] or [Scene 1].
5. Do NOT write markdown: no #, no *, no -, no bold, no italics.
6. Do NOT write scene numbers, timestamps, or section headers.
7. Do NOT write any description of visuals or actions.
8. Start IMMEDIATELY with the hook. No intro. No "welcome". No "in this video".
9. Every sentence must be spoken aloud. Nothing is for the eyes only.
10. Tone: calm, slow, confident, curious — like explaining to a 5-year-old child.
11. Use short sentences. Simple words. No jargon.
12. Total length: exactly {length}.

OUTPUT: Only the narration text. Nothing before it. Nothing after it. Begin now."""

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
                temperature=0.7,
                max_tokens=4000,
            )
            script = response.choices[0].message.content.strip()
            
            # Post-process: strip any accidental leading/trailing garbage
            script = script.replace("**", "").replace("##", "")
            script = script.replace("Voice:", "").replace("Narrator:", "")
            script = script.strip()
            
            # Remove lines that look like headers or labels
            cleaned_lines = []
            for line in script.split("\n"):
                stripped = line.strip()
                # Skip empty lines and label-only lines
                if not stripped:
                    continue
                if stripped.endswith(":") and len(stripped) < 40:
                    continue
                # Skip lines starting with markdown symbols
                if stripped.startswith(("#", "*", "-", "[")):
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

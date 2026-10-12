import os
import requests
from litellm import completion
from config import OPENROUTER_API_KEY, GROQ_API_KEY

# Set the API keys as environment variables for LiteLLM to find automatically
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY or ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""

def get_current_free_openrouter_models():
    """Fetches the live list of free models from OpenRouter at runtime."""
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        )
        response.raise_for_status()
        models = response.json().get("data", [])
        # Filter for models that are free (pricing prompt = "0")
        free_models = [
            m["id"] for m in models 
            if m.get("pricing", {}).get("prompt") == "0"
        ]
        print(f"🔍 Found {len(free_models)} free models on OpenRouter: {free_models[:5]}...")
        return free_models
    except Exception as e:
        print(f"⚠️ Could not fetch OpenRouter models: {repr(e)}")
        return []

def build_prompt(topic, video_type):
    if video_type == "long":
        return f"""
        Write a 10-minute YouTube script about: {topic}.
        Tone: Calm, confident, slow, curious, and simple. Explain it like you are talking to a 5-year-old child. 
        Hook: Start with a very exaggerated, curious hook in the first 10 seconds.
        Structure: Break it down into scenes. For each scene, write the voiceover text, and then in brackets, describe what the character should be doing (e.g., [Character scratching head], [Character looking shocked], [Character pointing up]).
        Make it engaging but soothing. Do not use complicated words.
        """
    else:
        return f"""
        Write a 45-second YouTube Short script about: {topic}.
        Tone: Fast-paced but calm, curious, simple, confident.
        Hook: Start with a shocking question.
        Structure: Voiceover text, and in brackets, the character's reaction (e.g., [Character shrugs], [Character smiles]).
        """

def write_script(topic, video_type="long"):
    print(f"✍️ Writing script for: {topic}")
    prompt = build_prompt(topic, video_type)

    # 1. Get the current list of free models from OpenRouter
    free_models = get_current_free_openrouter_models()
    
    # Build the fallback chain dynamically
    fallback_models = [f"openrouter/{m}" for m in free_models]
    
    # Add Groq as a backup if OpenRouter is down (using a currently supported model)
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
            script = response.choices[0].message.content
            print(f"✅ Script written by {model_name}")
            return script
        except Exception as e:
            print(f"⚠️ {model_name} failed: {repr(e)}")
            continue

    print("❌ All AI providers failed. Returning placeholder.")
    return f"Script generation failed for topic: {topic}"

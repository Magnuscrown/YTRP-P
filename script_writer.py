import os
from litellm import completion
from config import OPENROUTER_API_KEY, GROQ_API_KEY

# Set the API keys as environment variables for LiteLLM to find automatically
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY or ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""

# The fallback chain using OpenRouter's permanent :free aliases
FALLBACK_MODELS = [
    "openrouter/google/gemini-2.0-flash-exp:free",       # Permanent free alias for Gemini
    "openrouter/meta-llama/llama-3.3-70b-instruct:free", # Permanent free alias for Llama 3.3
    "groq/llama-3.3-70b-versatile"                       # Groq backup (if OpenRouter is down)
]

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

    for model_name in FALLBACK_MODELS:
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
            continue # Move to the next model in the list

    print("❌ All AI providers failed. Returning placeholder.")
    return f"Script generation failed for topic: {topic}"

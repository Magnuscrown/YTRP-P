import os
from litellm import completion
from config import GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY

# Set the API keys as environment variables for LiteLLM to find automatically
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY or ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY or ""
os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY or ""

# The fallback chain (LiteLLM handles the magic)
FALLBACK_MODELS = [
    "gemini/gemini-1.5-flash-latest",     # Try Google's current flash model
    "groq/llama-3.1-70b-versatile",       # Try Groq's current versatile model
    "openrouter/meta-llama/llama-3-70b-instruct", # Try OpenRouter
    "nvidia/meta/llama3-70b-instruct"     # Try NVIDIA
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

    # Try each model in the fallback chain manually so we can see which one worked
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

    # If all fail
    print("❌ All AI providers failed. Returning placeholder.")
    return f"Script generation failed for topic: {topic}"

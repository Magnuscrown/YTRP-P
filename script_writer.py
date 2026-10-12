import os
import requests
import google.generativeai as genai
from groq import Groq
from config import GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_API_KEY

# Debug: Check if keys are loaded
print(f"🔑 GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")
print(f"🔑 GROQ_API_KEY loaded: {bool(GROQ_API_KEY)}")
print(f"🔑 OPENROUTER_API_KEY loaded: {bool(OPENROUTER_API_KEY)}")
print(f"🔑 NVIDIA_API_KEY loaded: {bool(NVIDIA_API_KEY)}")

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

def generate_with_gemini(prompt):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except Exception as e:
        print(f"⚠️ Gemini failed: {repr(e)}")
        return None

def generate_with_groq(prompt):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Groq failed: {repr(e)}")
        return None

def generate_with_openrouter(prompt):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "meta-llama/llama-3-70b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"⚠️ OpenRouter failed: {repr(e)}")
        return None

def generate_with_nvidia(prompt):
    try:
        response = requests.post(
            url="https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            json={
                "model": "meta/llama3-70b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"⚠️ NVIDIA failed: {repr(e)}")
        return None

def write_script(topic, video_type="long"):
    print(f"✍️ Writing script for: {topic}")
    prompt = build_prompt(topic, video_type)

    script = generate_with_gemini(prompt)
    if script: 
        print("✅ Script written by Gemini")
        return script

    script = generate_with_groq(prompt)
    if script: 
        print("✅ Script written by Groq")
        return script

    script = generate_with_openrouter(prompt)
    if script: 
        print("✅ Script written by OpenRouter")
        return script

    script = generate_with_nvidia(prompt)
    if script: 
        print("✅ Script written by NVIDIA")
        return script

    print("❌ All AI providers failed. Returning placeholder.")
    return f"Script generation failed for topic: {topic}"

import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def write_script(topic, video_type="long"):
    print(f"✍️ Writing script for: {topic}")
    
    if video_type == "long":
        prompt = f"""
        Write a 10-minute YouTube script about: {topic}.
        Tone: Calm, slow, curious, and simple. Explain it like you are talking to a 5-year-old child. 
        Hook: Start with a very exaggerated, curious hook in the first 10 seconds.
        Structure: Break it down into scenes. For each scene, write the voiceover text, and then in brackets, describe what the character should be doing (e.g., [Character scratching head], [Character looking shocked], [Character pointing up]).
        Make it engaging but soothing. Do not use complicated words.
        """
    else: # Short
        prompt = f"""
        Write a 45-second YouTube Short script about: {topic}.
        Tone: Fast-paced but calm, very curious, simple.
        Hook: Start with a shocking question.
        Structure: Voiceover text, and in brackets, the character's reaction (e.g., [Character shrugs], [Character smiles]).
        """
        
    response = model.generate_content(prompt)
    return response.text

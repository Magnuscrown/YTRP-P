import re
import os
import asyncio
import requests
from config import OUTPUT_DIR, CF_ACCOUNT_ID, CF_API_TOKEN, CF_VOICE, CF_MODEL

def clean_script_for_voice(script_text):
    """Aggressively strips ALL markdown, symbols, and formatting before TTS."""
    text = script_text
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'[#*_`>]', '', text)
    text = re.sub(r'\s*[-–—]\s*', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_voice_cloudflare(text, output_path):
    """Cloudflare Aura TTS - natural, human-sounding MALE voice."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    
    max_chars = 1800
    chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    
    from moviepy.editor import concatenate_audioclips, AudioFileClip
    audio_chunks = []
    
    for i, chunk in enumerate(chunks):
        payload = {"text": chunk, "speaker": CF_VOICE, "encoding": "mp3"}
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        if response.status_code != 200:
            raise Exception(f"Cloudflare error {response.status_code}: {response.text[:200]}")
        
        chunk_path = f"{output_path}.part{i}.mp3"
        with open(chunk_path, "wb") as f:
            f.write(response.content)
        audio_chunks.append(chunk_path)
        print(f"   ✔️ Chunk {i+1}/{len(chunks)} done")
    
    if len(audio_chunks) == 1:
        os.rename(audio_chunks[0], output_path)
    else:
        clips = [AudioFileClip(c) for c in audio_chunks]
        final = concatenate_audioclips(clips)
        final.write_audiofile(output_path, logger=None)
        for c in audio_chunks:
            os.remove(c)
    return output_path

def generate_voice_pyttsx3(text, output_path):
    """Offline TTS fallback using pyttsx3 (no internet needed)."""
    import pyttsx3
    engine = pyttsx3.init()
    # Try to find a male voice
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'male' in voice.name.lower() or 'guy' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)  # Slower, calmer
    engine.setProperty('volume', 1.0)
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def generate_voiceover(script_text, output_filename):
    print(f"🎙️ Generating MALE voiceover: {output_filename}...")
    clean_text = clean_script_for_voice(script_text)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Try Cloudflare Aura first (best quality)
    try:
        generate_voice_cloudflare(clean_text, output_path)
        print(f"✅ Natural male voice saved via Cloudflare: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Cloudflare TTS failed: {repr(e)}")
    
    # Fallback to offline pyttsx3 (never blocked)
    try:
        generate_voice_pyttsx3(clean_text, output_path)
        print(f"✅ Offline male voice saved via pyttsx3: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ All TTS failed: {repr(e)}")
        raise

def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

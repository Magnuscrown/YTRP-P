import re
import os
import asyncio
import requests
from config import OUTPUT_DIR, CF_ACCOUNT_ID, CF_API_TOKEN, CF_VOICE, CF_MODEL, BACKUP_VOICE

def clean_script_for_voice(script_text):
    """Aggressively strips ALL markdown, symbols, and formatting before TTS."""
    text = script_text
    text = re.sub(r'\[.*?\]', '', text)          # Remove [Character smiles]
    text = re.sub(r'\(.*?\)', '', text)          # Remove (parenthetical)
    text = re.sub(r'[#*_`>]', '', text)          # Remove markdown symbols
    text = re.sub(r'\s*[-–—]\s*', ' ', text)     # Remove dashes
    text = re.sub(r'\.{2,}', '.', text)          # Collapse ...
    text = re.sub(r'!{2,}', '!', text)           # Collapse !!!
    text = re.sub(r'\?{2,}', '?', text)          # Collapse ???
    text = re.sub(r'\s+', ' ', text)             # Collapse whitespace
    return text.strip()

def generate_voice_cloudflare(text, output_path):
    """Cloudflare Aura TTS - natural, human-sounding MALE voice."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    
    # Aura has a character limit, chunk it safely
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
    
    # Merge chunks
    if len(audio_chunks) == 1:
        os.rename(audio_chunks[0], output_path)
    else:
        clips = [AudioFileClip(c) for c in audio_chunks]
        final = concatenate_audioclips(clips)
        final.write_audiofile(output_path, logger=None)
        for c in audio_chunks:
            os.remove(c)
    return output_path

def generate_voice_edge(text, output_path):
    """Fallback: edge-tts male voice."""
    import edge_tts
    async def _run():
        communicate = edge_tts.Communicate(text, BACKUP_VOICE, rate="-12%", pitch="-2Hz")
        await communicate.save(output_path)
    asyncio.run(_run())
    return output_path

def generate_voiceover(script_text, output_filename):
    print(f"🎙️ Generating MALE voiceover: {output_filename}...")
    clean_text = clean_script_for_voice(script_text)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Try Cloudflare Aura (best quality male)
    try:
        generate_voice_cloudflare(clean_text, output_path)
        print(f"✅ Natural male voice saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Cloudflare TTS failed: {repr(e)}")
    
    # Fallback to edge-tts male voice
    try:
        generate_voice_edge(clean_text, output_path)
        print(f"✅ Backup male voice saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ All TTS failed: {repr(e)}")
        raise

def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

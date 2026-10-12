import edge_tts
import re
import os
from config import VOICE_NAME, VOICE_RATE, VOICE_PITCH, OUTPUT_DIR

def clean_script_for_voice(script_text):
    """Removes bracketed character actions like [Character smiles] before TTS."""
    cleaned = re.sub(r'\[.*?\]', '', script_text)
    return cleaned.strip()

async def generate_voiceover(script_text, output_filename):
    print(f"🎙️ Generating voiceover for {output_filename}...")
    clean_text = clean_script_for_voice(script_text)
    
    communicate = edge_tts.Communicate(
        clean_text, 
        VOICE_NAME, 
        rate=VOICE_RATE, 
        pitch=VOICE_PITCH
    )
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    await communicate.save(output_path)
    print(f"✅ Voiceover saved: {output_path}")
    return output_path

# Helper to run async function from synchronous code
import asyncio
def make_voice(script_text, output_filename):
    asyncio.run(generate_voiceover(script_text, output_filename))

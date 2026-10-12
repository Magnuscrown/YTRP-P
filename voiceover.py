import re
import os
from gtts import gTTS
from config import OUTPUT_DIR

def clean_script_for_voice(script_text):
    """Removes bracketed character actions like [Character smiles] before TTS."""
    cleaned = re.sub(r'\[.*?\]', '', script_text)
    return cleaned.strip()

def generate_voiceover(script_text, output_filename):
    print(f"🎙️ Generating voiceover for {output_filename}...")
    clean_text = clean_script_for_voice(script_text)
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        # gTTS uses Google's TTS engine. 'slow=True' makes it calmer and slower.
        tts = gTTS(text=clean_text, lang='en', slow=True)
        tts.save(output_path)
        print(f"✅ Voiceover saved with gTTS: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ gTTS failed: {e}")
        
        # Fallback to edge-tts
        try:
            import edge_tts
            import asyncio
            from config import VOICE_NAME, VOICE_RATE, VOICE_PITCH
            
            async def _edge_tts():
                communicate = edge_tts.Communicate(
                    clean_text, 
                    VOICE_NAME, 
                    rate=VOICE_RATE, 
                    pitch=VOICE_PITCH
                )
                await communicate.save(output_path)
            
            asyncio.run(_edge_tts())
            print(f"✅ Voiceover saved with edge-tts fallback: {output_path}")
            return output_path
        except Exception as e2:
            print(f"❌ All TTS providers failed: {e2}")
            raise

def make_voice(script_text, output_filename):
    """Synchronous wrapper for the voiceover generation."""
    return generate_voiceover(script_text, output_filename)

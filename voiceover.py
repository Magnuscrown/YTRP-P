import re
import os
import wave
from piper import PiperVoice
from config import OUTPUT_DIR

PIPER_MODEL = "piper_voices/en_US-ryan-high.onnx"

def clean_script_for_voice(script_text):
    """Aggressively strips ALL markdown, symbols, and formatting."""
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

def generate_voiceover(script_text, output_filename):
    """Piper TTS - natural male voice, runs on CPU, no internet needed."""
    print(f"🎙️ Generating voiceover: {output_filename}...")
    clean_text = clean_script_for_voice(script_text)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    if not os.path.exists(PIPER_MODEL):
        raise Exception(f"Piper model not found at {PIPER_MODEL}")
    
    voice = PiperVoice.load(PIPER_MODEL)
    
    # Piper outputs WAV, we need MP3 for MoviePy. We'll save WAV first.
    wav_path = output_path.replace(".mp3", ".wav")
    
    with wave.open(wav_path, "wb") as wav_file:
        voice.synthesize(clean_text, wav_file)
    
    # Convert WAV to MP3 using MoviePy
    from moviepy.editor import AudioFileClip
    audio = AudioFileClip(wav_path)
    audio.write_audiofile(output_path, logger=None)
    audio.close()
    os.remove(wav_path)
    
    print(f"✅ Voice saved: {output_path}")
    return output_path

def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

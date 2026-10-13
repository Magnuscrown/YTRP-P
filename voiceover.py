import re
import os
import wave
from piper import PiperVoice, SynthesisConfig
from config import OUTPUT_DIR

PIPER_MODEL = "piper_voices/en_US-ryan-high.onnx"

def clean_script_for_voice(script_text):
    """Strip any remaining junk before TTS."""
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

def generate_voiceover(script_text, output_filename, slow_factor=1.18):
    """Piper TTS with slower speed. slow_factor > 1.0 = slower."""
    print(f"🎙️ Generating voiceover: {output_filename} (slow: {slow_factor}x)...")
    clean_text = clean_script_for_voice(script_text)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    if not os.path.exists(PIPER_MODEL):
        raise Exception(f"Piper model not found at {PIPER_MODEL}")
    
    voice = PiperVoice.load(PIPER_MODEL)
    wav_path = output_path.replace(".mp3", "_raw.wav")
    
    # Try using SynthesisConfig to slow the voice natively (best quality)
    try:
        syn_config = SynthesisConfig(length_scale=slow_factor)
        with wave.open(wav_path, "wb") as wav_file:
            voice.synthesize(clean_text, wav_file, syn_config=syn_config)
        print(f"   ✔️ Synthesized with length_scale={slow_factor}")
    except Exception as e:
        print(f"   ⚠️ SynthesisConfig not supported, falling back: {repr(e)[:120]}")
        with wave.open(wav_path, "wb") as wav_file:
            voice.synthesize(clean_text, wav_file)
    
    # Convert WAV → MP3
    from moviepy.editor import AudioFileClip
    audio = AudioFileClip(wav_path)
    audio.write_audiofile(output_path, logger=None)
    audio.close()
    os.remove(wav_path)
    
    print(f"✅ Voice saved: {output_path}")
    return output_path

def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

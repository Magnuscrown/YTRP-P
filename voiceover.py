import re
import os
import wave
import subprocess
from piper import PiperVoice
from config import OUTPUT_DIR

PIPER_MODEL = "piper_voices/en_US-ryan-high.onnx"

def clean_script_for_voice(script_text):
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


def synthesize_with_piper(text, wav_path):
    """Try every known Piper API shape until one works."""
    voice = PiperVoice.load(PIPER_MODEL)
    
    # 1. Try with SynthesisConfig (piper >= 1.3)
    try:
        from piper import SynthesisConfig
        syn = SynthesisConfig(length_scale=1.18)
        with wave.open(wav_path, "wb") as wav_file:
            voice.synthesize(text, wav_file, syn_config=syn)
        print("   ✔️ Used SynthesisConfig API")
        return
    except Exception as e:
        print(f"   ⚠️ SynthesisConfig API failed: {repr(e)[:120]}")
    
    # 2. Try simple two-arg API (piper 1.2.x)
    try:
        with wave.open(wav_path, "wb") as wav_file:
            voice.synthesize(text, wav_file)
        print("   ✔️ Used simple API")
        return
    except Exception as e:
        print(f"   ⚠️ Simple API failed: {repr(e)[:120]}")
        raise


def slow_down_and_convert(wav_path, mp3_path, speed=0.88):
    """Uses ffmpeg to slow the audio (speed<1 = slower) and convert to mp3."""
    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-filter:a", f"atempo={speed}",
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "4",
        mp3_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ffmpeg failed: {result.stderr[-300:]}")


def generate_voiceover(script_text, output_filename, slow_factor=0.88):
    print(f"🎙️ Generating voiceover: {output_filename} (slowing to {slow_factor}x)...")
    clean_text = clean_script_for_voice(script_text)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    if not os.path.exists(PIPER_MODEL):
        raise Exception(f"Piper model not found at {PIPER_MODEL}")
    
    wav_path = output_path.replace(".mp3", "_raw.wav")
    
    # 1. Synthesize with Piper (fast, native speed)
    synthesize_with_piper(clean_text, wav_path)
    
    # 2. Slow down with ffmpeg (0.88 = 12% slower, natural pitch)
    slow_down_and_convert(wav_path, output_path, speed=slow_factor)
    
    # 3. Clean up WAV
    if os.path.exists(wav_path):
        os.remove(wav_path)
    
    print(f"✅ Voice saved: {output_path}")
    return output_path


def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

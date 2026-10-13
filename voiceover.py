import re
import os
import wave
from piper import PiperVoice, SynthesisConfig
from config import OUTPUT_DIR, PIPER_MODEL, VOICE_SLOW_FACTOR


def clean_script_for_voice(text):
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
    print(f"🎙️ Voice: {output_filename}...")
    clean = clean_script_for_voice(script_text)
    out = os.path.join(OUTPUT_DIR, output_filename)
    wav = out.replace(".mp3", "_raw.wav")

    if not os.path.exists(PIPER_MODEL):
        raise Exception(f"Piper model missing: {PIPER_MODEL}")

    voice = PiperVoice.load(PIPER_MODEL)

    try:
        cfg = SynthesisConfig(length_scale=VOICE_SLOW_FACTOR)
        with wave.open(wav, "wb") as f:
            voice.synthesize(clean, f, syn_config=cfg)
    except Exception as e:
        print(f"⚠️ SynthesisConfig unsupported: {repr(e)[:120]}")
        with wave.open(wav, "wb") as f:
            voice.synthesize(clean, f)

    from moviepy.editor import AudioFileClip
    a = AudioFileClip(wav)
    a.write_audiofile(out, logger=None)
    a.close()
    os.remove(wav)
    print(f"✅ Voice saved: {out}")
    return out


def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

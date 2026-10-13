import re
import os
import wave
from piper import PiperVoice
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

    # Try to load SynthesisConfig (optional — older versions don't have it)
    cfg = None
    try:
        from piper import SynthesisConfig
        cfg = SynthesisConfig(length_scale=VOICE_SLOW_FACTOR)
        print(f"   ✔️ SynthesisConfig loaded (slow_factor={VOICE_SLOW_FACTOR})")
    except ImportError:
        print(f"   ⚠️ SynthesisConfig not available — using default speed")

    wrote_ok = False

    # --- Try new API first: synthesize_wav(text, wav_file, syn_config=...) ---
    if hasattr(voice, "synthesize_wav"):
        try:
            with wave.open(wav, "wb") as f:
                if cfg is not None:
                    voice.synthesize_wav(clean, f, syn_config=cfg)
                else:
                    voice.synthesize_wav(clean, f)
            wrote_ok = True
            print(f"   ✔️ Used synthesize_wav (new API)")
        except Exception as e:
            print(f"   ⚠️ synthesize_wav failed: {repr(e)[:120]}")

    # --- Fall back to old API: synthesize(text, wav_file) ---
    if not wrote_ok:
        try:
            with wave.open(wav, "wb") as f:
                voice.synthesize(clean, f)
            wrote_ok = True
            print(f"   ✔️ Used synthesize (old API)")
        except Exception as e:
            print(f"   ⚠️ synthesize failed: {repr(e)[:120]}")

    if not wrote_ok:
        raise Exception("All Piper voice APIs failed")

    # Convert WAV → MP3
    from moviepy.editor import AudioFileClip
    a = AudioFileClip(wav)
    a.write_audiofile(out, logger=None)
    a.close()
    os.remove(wav)
    print(f"✅ Voice saved: {out}")
    return out


def make_voice(script_text, output_filename):
    return generate_voiceover(script_text, output_filename)

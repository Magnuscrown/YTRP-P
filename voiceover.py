"""Piper TTS, sentence by sentence, so every scene can be synced to the real audio timing."""
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from config import PIPER_MODEL, PIPER_LENGTH_SCALE, SENTENCE_PAUSE

_voice = None
_cfg = None


def _load():
    global _voice, _cfg
    if _voice is None:
        from piper import PiperVoice
        _voice = PiperVoice.load(PIPER_MODEL)
        try:
            from piper import SynthesisConfig
            _cfg = SynthesisConfig(length_scale=PIPER_LENGTH_SCALE)
        except Exception:
            _cfg = None
    return _voice


def prep(text):
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)
    text = re.sub(r"[#*_>`~|]", " ", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r",\s*,+", ",", text)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", prep(text))
    return [p.strip() for p in parts if len(re.sub(r"\W", "", p)) > 1]


def _synth(text, path):
    voice = _load()
    try:
        with wave.open(str(path), "wb") as wf:
            voice.synthesize_wav(text, wf, syn_config=_cfg)
        return
    except (AttributeError, TypeError):
        pass
    for flag in ("--length-scale", "--length_scale"):   # CLI fallback
        r = subprocess.run([sys.executable, "-m", "piper", "-m", PIPER_MODEL, "-f", str(path), flag,
                            str(PIPER_LENGTH_SCALE)], input=text.encode(), capture_output=True)
        if r.returncode == 0 and Path(path).exists():
            return
    raise RuntimeError("Piper synthesis failed")


def synthesize(script, work_dir, tag="voice"):
    """Returns (mp3_path, sentences, durations_in_seconds_per_sentence_including_pause)."""
    work_dir = Path(work_dir)
    sentences = split_sentences(script)
    arrays, durations, sr = [], [], None
    for i, s in enumerate(sentences):
        wav = work_dir / f"{tag}_{i}.wav"
        _synth(s, wav)
        with wave.open(str(wav), "rb") as wf:
            sr = wf.getframerate()
            arr = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        wav.unlink()
        pause = np.zeros(int(sr * SENTENCE_PAUSE), dtype=np.int16)
        arrays += [arr, pause]
        durations.append((len(arr) + len(pause)) / sr)
    full = work_dir / f"{tag}.wav"
    with wave.open(str(full), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(np.concatenate(arrays).tobytes())
    mp3 = work_dir / f"{tag}.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(full), "-codec:a", "libmp3lame",
                    "-q:a", "4", str(mp3)], check=True)
    full.unlink()
    print(f"[voice] {len(sentences)} sentences, {sum(durations):.0f}s ({sum(durations) / 60:.1f} min)")
    return str(mp3), sentences, durations

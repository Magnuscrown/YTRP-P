import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
WORK_DIR = ROOT / "work"
USED_TOPICS_FILE = ROOT / "used_topics.json"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")

# ---- Voice (Piper) ----
PIPER_MODEL = os.getenv("PIPER_MODEL", str(ROOT / "models" / "en_US-hfc_male-medium.onnx"))
PIPER_LENGTH_SCALE = 1.30      # 30% slower = calm, patient
SENTENCE_PAUSE = 0.25          # seconds of silence after each sentence

# ---- Images (Cloudflare Workers AI) ----
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
IMAGE_WORKERS = 3

# ---- Video ----
FPS = 24
SCENE_MIN_SEC = 3.0            # every image stays on screen 3-5 seconds
SCENE_MAX_SEC = 5.0

SPECS = {
    "long": {
        "size": (1920, 1080),          # 16:9
        "words_target_total": 2400,    # ~17 min at Piper 1.30
        "words_hard_min": 1400,        # ~10 min
        "min_sec": 840,                # accept if >= 14 min (normal = 15-20 min)
        "hard_min_sec": 600,           # never below 10 min (warn if it happens)
        "max_sec": 1500,
        "max_images": 100,             # unique images per video (rest are reused)
        "script_attempts": 2,
    },
    "short": {
        "size": (1080, 1920),          # 9:16
        "words_target": (190, 270),
        "words_accept": (150, 330),
        "min_sec": 60,                 # 1:00
        "max_sec": 149,                # 2:29
        "max_images": 25,
        "script_attempts": 3,
    },
}

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
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# ---- Voice (Piper) ----
PIPER_MODEL = os.getenv("PIPER_MODEL", str(ROOT / "models" / "en_US-hfc_male-medium.onnx"))
PIPER_LENGTH_SCALE = 1.30      # slow and clear. Higher = slower (1.40 sounds dragged)
SENTENCE_PAUSE = 0.45          # longer pauses between sentences feel more human

# ---- Video ----
FPS = 20
SUPERSAMPLE = 2
SCENE_MIN_SEC = 5.0
SCENE_MAX_SEC = 7.0
TEXT_SCENE_USE_WHITE = True
TEXT_SCENE_CHANCE = 0.10
STICKER_CHANCE = 0.35

# ---- Channel Focus: Rich vs Poor Psychology ----
CHANNEL_FOCUS = "psychology"   # Options: "psychology" or "general"

SPECS = {
    "long": {
        "size": (1280, 720),
        "words_target_total": 2700,
        "words_hard_min": 1200,
        "min_sec": 840,
        "hard_min_sec": 600,
        "max_sec": 1500,
        "script_attempts": 2,
        "n_range": (6, 10),
    },
    "short": {
        "size": (720, 1280),
        "words_target": (190, 270),
        "words_accept": (150, 330),
        "min_sec": 60,
        "max_sec": 149,
        "script_attempts": 3,
        "n_range": (3, 5),
    },
}

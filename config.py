import os

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

# Output
OUTPUT_DIR = "output"

# Video dimensions
LONG_WIDTH, LONG_HEIGHT = 1920, 1080
SHORT_WIDTH, SHORT_HEIGHT = 1080, 1920

# Voice (Piper)
PIPER_MODEL = "piper_voices/en_US-ryan-high.onnx"
VOICE_SLOW_FACTOR = 1.18   # 18% slower

# Visuals
IMAGE_STYLE = (
    "cinematic photorealistic, dramatic lighting, "
    "shallow depth of field, moody atmosphere, "
    "detailed textures, film grain, professional photography, "
    "no text, no watermark, no people faces close-up"
)

# How many images per video (fewer = longer zoom per image)
IMAGES_LONG = 30
IMAGES_SHORT = 5

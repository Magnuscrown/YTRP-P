import os

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

# Output Settings
OUTPUT_DIR = "output"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
SHORT_WIDTH = 1080
SHORT_HEIGHT = 1920

# Character Settings (The "Magnus" Character)
CHARACTER_PROMPT = "2D vector cartoon character, white male, short brown hair, wearing a red hoodie and blue jeans, big black expressive eyes, simple stick figure body, clean white background, consistent character design"

# Voice Settings (Calm, slow, natural, confident)
VOICE_NAME = "en-US-ChristopherNeural"
VOICE_RATE = "-15%" # Slower
VOICE_PITCH = "-2Hz" # Slightly deeper

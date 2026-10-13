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

# Cloudflare Aura Voice Settings (MALE, natural, calm)
CF_VOICE = "apollo"          # Male, deep, calm narrator voice
CF_MODEL = "@cf/deepgram/aura-1"

# Backup TTS Settings (if Cloudflare fails)
BACKUP_VOICE = "en-US-GuyNeural"  # Male Microsoft voice

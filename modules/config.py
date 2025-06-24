"""Configuration settings for My Manga Recap - Centralized config with .env support."""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# Directory settings
DEFAULT_TEMP_DIR = "temp"

# Language and video settings
DEFAULT_LANG = "pt"
DEFAULT_IMAGE_DURATION = None  # Auto-calculated based on audio
DEFAULT_VIDEO_WIDTH = 1280
DEFAULT_VIDEO_HEIGHT = 720

# OpenAI Configuration (loaded from .env or environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")

# Configuration validation and info
def get_openai_config():
    """Get OpenAI configuration as a dictionary"""
    return {
        "api_key": OPENAI_API_KEY,
        "model": OPENAI_MODEL,
        "tts_model": OPENAI_TTS_MODEL,
        "tts_voice": OPENAI_TTS_VOICE
    }

def is_openai_configured():
    """Check if OpenAI is properly configured"""
    return OPENAI_API_KEY is not None and OPENAI_API_KEY.strip() != ""

def print_config_status():
    """Print current configuration status"""
    print("⚙️  Configuração Atual:")
    print(f"  OPENAI_API_KEY: {'✅ Configurada' if is_openai_configured() else '❌ Não encontrada'}")
    print(f"  OPENAI_MODEL: {OPENAI_MODEL}")
    print(f"  OPENAI_TTS_MODEL: {OPENAI_TTS_MODEL}")
    print(f"  OPENAI_TTS_VOICE: {OPENAI_TTS_VOICE}")
    if not is_openai_configured():
        print("💡 Dica: Copie env.example para .env e configure sua API key")

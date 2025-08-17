import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
CACHE_DIR = BASE_DIR / "cache"

# Configurações OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")

# Configurações de idioma
DEFAULT_LANGUAGE = os.getenv("MMR_LANG", "pt")

# Configurações de vídeo
DEFAULT_VIDEO_WIDTH = 1280
DEFAULT_VIDEO_HEIGHT = 720
DEFAULT_FPS = 30

# Configurações de cache
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hora em segundos

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Configurações de OCR
OCR_PROVIDER_PRIORITY = ["openai", "trocr", "tesseract"]

# Criação de diretórios necessários
for directory in [TEMP_DIR, CACHE_DIR, LOG_FILE.parent]:
    directory.mkdir(parents=True, exist_ok=True) 
from enum import Enum, auto

class ProviderType(Enum):
    """Tipos de provedores disponíveis no sistema"""
    OPENAI = auto()
    LOCAL = auto()
    SILENT = auto()

class OCRProvider(Enum):
    """Provedores de OCR disponíveis"""
    OPENAI_VISION = auto()
    TROCR = auto()
    TESSERACT = auto()

class TTSVoice(Enum):
    """Vozes disponíveis para TTS"""
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

# Extensões de arquivo suportadas
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Configurações de timeout
DEFAULT_TIMEOUT = 30  # segundos
LONG_TIMEOUT = 120    # segundos

# Configurações de retry
MAX_RETRIES = 3
RETRY_DELAY = 1  # segundos

# Templates de prompt
PROMPT_TEMPLATES = {
    "script_gen": """Gere um roteiro narrativo para a seguinte cena do mangá:
{text}

Considere o contexto: {context}
""",
    "scene_analysis": """Analise a seguinte cena e descreva:
1. Personagens presentes
2. Ações principais
3. Ambiente/cenário
4. Tom emocional

Cena: {text}
""",
}

# Configurações de áudio
AUDIO_SETTINGS = {
    "sample_rate": 44100,
    "channels": 2,
    "format": "mp3",
} 
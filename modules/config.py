"""Configuration settings for MangaRecap."""

DEFAULT_TEMP_DIR = "temp"
DEFAULT_MODEL = "google/flan-t5-base"
DEFAULT_PROMPT = (
    "Resuma o seguinte texto de forma narrativa. Utilize '[PAUSA]' para"
    " indicar pausas e sugira imagens no formato [IMAGEM: descricao]."
)
DEFAULT_LANG = "pt"
DEFAULT_VOICE = None
DEFAULT_IMAGE_DURATION = None
DEFAULT_USE_TTS = False
DEFAULT_VIDEO_WIDTH = 1280
DEFAULT_VIDEO_HEIGHT = 720

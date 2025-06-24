"""
My Manga Recap - Modules Package

Sistema modular para conversão de mangás em vídeos narrados com IA.

Módulos disponíveis:
- ai_provider: Sistema adaptável de provedores de IA (OpenAI, Local, Silent)
- ocr: Extração de texto de imagens de mangá
- script_narrator: Geração de roteiros usando AI providers
- audio_gen: Síntese de voz usando AI providers
- video_gen: Criação de vídeos sincronizados
- config: Configurações do sistema
"""

__version__ = "2.0.0"
__author__ = "My Manga Recap Team"

# Principais classes/funções exportadas
from .ai_provider import AIManager, OpenAIProvider, LocalProvider, SilentProvider
from .ocr import extract_text_from_chapter
from .script_narrator import generate_scripts_from_ocr
from .audio_gen import text_to_speech
from .video_gen import create_video

__all__ = [
    "AIManager", 
    "OpenAIProvider", 
    "LocalProvider", 
    "SilentProvider",
    "extract_text_from_chapter",
    "generate_scripts_from_ocr", 
    "text_to_speech",
    "create_video"
]

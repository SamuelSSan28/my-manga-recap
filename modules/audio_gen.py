"""
Audio Generation Module - Simplified
Uses the new AI provider system for TTS
"""

from typing import Optional
from .ai_provider import AIManager


def text_to_speech(
    script: str,
    output_path: str,
    lang: str = "pt",
    voice_name: Optional[str] = None,
    use_tts: bool = False,
) -> None:
    """Generate speech audio from text using AI providers."""

    if not script.strip():
        print("⚠️  Script vazio!")
        return

    print(f"🎤 Gerando áudio para script de {len(script.split())} palavras...")

    # Use AI manager to generate audio
    ai_manager = AIManager()
    success = ai_manager.generate_audio(script, output_path, lang)
    
    if success:
        print("✅ Áudio gerado com sucesso!")
    else:
        print("❌ Falha na geração de áudio")

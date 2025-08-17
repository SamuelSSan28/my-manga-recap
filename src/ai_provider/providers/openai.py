import base64
from pathlib import Path
from typing import Dict, Any, List, Optional

import openai
from openai import OpenAI

from ...config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TTS_MODEL,
    OPENAI_TTS_VOICE,
    OPENAI_VISION_MODEL
)
from ...config.constants import PROMPT_TEMPLATES
from ..base import AIProvider
from ...utils.logger import get_logger
from ...utils.cache import cached

logger = get_logger(__name__)

class OpenAIProvider(AIProvider):
    """Provider que utiliza serviços da OpenAI"""
    
    def __init__(self):
        self._client = OpenAI(api_key=OPENAI_API_KEY)
        self._available = bool(OPENAI_API_KEY)
    
    @cached("openai_script")
    def generate_script(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Gera roteiro usando GPT"""
        if not self.is_available:
            raise RuntimeError("OpenAI API key não configurada")
            
        context = context or {}
        prompt = PROMPT_TEMPLATES["script_gen"].format(
            text=text,
            context=context
        )
        
        try:
            response = self._client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um roteirista especializado em adaptar mangás para vídeos narrados."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar roteiro: {e}")
            raise
    
    @cached("openai_audio")
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """Gera áudio usando OpenAI TTS"""
        if not self.is_available:
            raise RuntimeError("OpenAI API key não configurada")
            
        try:
            response = self._client.audio.speech.create(
                model=OPENAI_TTS_MODEL,
                voice=OPENAI_TTS_VOICE,
                input=text
            )
            
            # Salva o áudio
            output_path.parent.mkdir(parents=True, exist_ok=True)
            response.stream_to_file(str(output_path))
            
            return output_path
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            raise
    
    @cached("openai_ocr")
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extrai texto usando Vision API"""
        if not self.is_available:
            raise RuntimeError("OpenAI API key não configurada")
            
        try:
            # Codifica a imagem em base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self._client.chat.completions.create(
                model=OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extraia todo o texto desta imagem de mangá, incluindo diálogos e onomatopeias."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            return {
                "text": response.choices[0].message.content,
                "confidence": 0.95  # OpenAI não fornece score
            }
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            raise
    
    @cached("openai_scene")
    def analyze_scene(self, image_path: Path, text: str) -> Dict[str, Any]:
        """Analisa a cena usando Vision API"""
        if not self.is_available:
            raise RuntimeError("OpenAI API key não configurada")
            
        try:
            # Codifica a imagem em base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = PROMPT_TEMPLATES["scene_analysis"].format(text=text)
            
            response = self._client.chat.completions.create(
                model=OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "confidence": 0.95
            }
        except Exception as e:
            logger.error(f"Erro ao analisar cena: {e}")
            raise
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    @property
    def capabilities(self) -> List[str]:
        return ["script", "audio", "ocr", "scene_analysis"] 
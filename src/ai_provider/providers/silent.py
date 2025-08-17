from pathlib import Path
import wave
import struct
from typing import Dict, Any, List, Optional

from ..base import AIProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

class SilentProvider(AIProvider):
    """Provider que gera áudio silencioso como fallback"""
    
    def __init__(self):
        self._available = True
    
    def generate_script(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Retorna o texto como está"""
        return text
    
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """
        Gera um arquivo de áudio silencioso com duração baseada no texto.
        Usa uma heurística simples: 0.3 segundos por palavra.
        """
        try:
            # Calcula duração baseada no número de palavras
            words = len(text.split())
            duration = max(1.0, words * 0.3)  # Mínimo 1 segundo
            
            # Parâmetros do áudio
            sample_rate = 44100
            num_channels = 2
            sample_width = 2  # 16 bits
            
            # Cria diretório se necessário
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Gera arquivo WAV silencioso
            with wave.open(str(output_path), 'w') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                
                # Gera amostras silenciosas (valor zero)
                num_samples = int(duration * sample_rate)
                samples = struct.pack(f'<{num_samples * num_channels}h', *([0] * (num_samples * num_channels)))
                wav_file.writeframes(samples)
            
            return output_path
        except Exception as e:
            logger.error(f"Erro ao gerar áudio silencioso: {e}")
            raise
    
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Retorna texto vazio com confiança zero"""
        return {
            "text": "",
            "confidence": 0.0
        }
    
    def analyze_scene(self, image_path: Path, text: str) -> Dict[str, Any]:
        """Retorna análise vazia"""
        return {
            "analysis": {
                "description": "Análise não disponível",
                "text_content": text,
                "has_text": bool(text.strip())
            },
            "confidence": 0.0
        }
    
    @property
    def name(self) -> str:
        return "Silent"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    @property
    def capabilities(self) -> List[str]:
        return ["audio"]  # Só oferece geração de áudio silencioso 
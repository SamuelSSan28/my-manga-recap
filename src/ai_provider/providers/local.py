from pathlib import Path
from typing import Dict, Any, List, Optional
import pyttsx3
import pytesseract
from PIL import Image

from ..base import AIProvider
from ...utils.logger import get_logger
from ...utils.cache import cached

logger = get_logger(__name__)

class LocalProvider(AIProvider):
    """Provider que utiliza ferramentas locais"""
    
    def __init__(self):
        # Inicializa TTS
        try:
            self._tts_engine = pyttsx3.init()
            self._tts_available = True
        except Exception as e:
            logger.error(f"Erro ao inicializar TTS: {e}")
            self._tts_available = False
        
        # Verifica Tesseract
        try:
            pytesseract.get_tesseract_version()
            self._ocr_available = True
        except Exception as e:
            logger.error(f"Erro ao verificar Tesseract: {e}")
            self._ocr_available = False
    
    @cached("local_script")
    def generate_script(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Gera um roteiro simples baseado no texto extraído"""
        context = context or {}
        
        # Template simples para roteiro
        script = f"""
Cena:
{text}

Contexto adicional:
{context.get('description', 'Sem contexto adicional')}

Narração:
{text}
""".strip()
        
        return script
    
    @cached("local_audio")
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """Gera áudio usando pyttsx3"""
        if not self._tts_available:
            raise RuntimeError("TTS local não disponível")
        
        try:
            # Configura saída
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._tts_engine.save_to_file(text, str(output_path))
            self._tts_engine.runAndWait()
            
            return output_path
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            raise
    
    @cached("local_ocr")
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extrai texto usando Tesseract"""
        if not self._ocr_available:
            raise RuntimeError("Tesseract não disponível")
        
        try:
            # Carrega e prepara a imagem
            image = Image.open(image_path)
            
            # Extrai texto
            text = pytesseract.image_to_string(image, lang='por')
            
            # Calcula confiança
            confidence = float(
                pytesseract.image_to_data(
                    image, 
                    lang='por', 
                    output_type=pytesseract.Output.DICT
                )['conf'][0]
            ) / 100
            
            return {
                "text": text.strip(),
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            raise
    
    @cached("local_scene")
    def analyze_scene(self, image_path: Path, text: str) -> Dict[str, Any]:
        """Análise básica da cena"""
        try:
            # Análise simples baseada no texto extraído
            analysis = {
                "description": "Cena de mangá com texto extraído",
                "text_content": text,
                "has_text": bool(text.strip())
            }
            
            return {
                "analysis": analysis,
                "confidence": 0.7
            }
        except Exception as e:
            logger.error(f"Erro ao analisar cena: {e}")
            raise
    
    @property
    def name(self) -> str:
        return "Local"
    
    @property
    def is_available(self) -> bool:
        return self._tts_available and self._ocr_available
    
    @property
    def capabilities(self) -> List[str]:
        caps = []
        if self._tts_available:
            caps.append("audio")
        if self._ocr_available:
            caps.extend(["ocr", "script"])
        return caps 
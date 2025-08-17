from pathlib import Path
from typing import Dict, Any
import pytesseract
from PIL import Image

from ..base import OCRProvider
from ...utils.logger import get_logger
from ...utils.cache import cached

logger = get_logger(__name__)

class TesseractProvider(OCRProvider):
    """Provider que usa Tesseract OCR"""
    
    def __init__(self):
        try:
            self._version = pytesseract.get_tesseract_version()
            self._available = True
            
            # Lista idiomas disponíveis
            self._languages = {
                lang: True for lang in pytesseract.get_languages()
            }
        except Exception as e:
            logger.error(f"Erro ao inicializar Tesseract: {e}")
            self._available = False
            self._languages = {}
    
    @cached("tesseract_ocr")
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extrai texto usando Tesseract"""
        if not self.is_available:
            raise RuntimeError("Tesseract não está disponível")
        
        try:
            # Carrega imagem
            image = Image.open(image_path)
            
            # Extrai texto e dados
            data = pytesseract.image_to_data(
                image,
                lang='por+eng+jpn',  # Tenta múltiplos idiomas
                output_type=pytesseract.Output.DICT
            )
            
            # Filtra boxes válidos
            valid_boxes = []
            text_parts = []
            total_conf = 0
            count = 0
            
            for i, conf in enumerate(data['conf']):
                if conf > 0:  # Ignora confiança negativa
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        total_conf += conf
                        count += 1
                        
                        # Adiciona bounding box
                        valid_boxes.append({
                            'text': text,
                            'confidence': conf,
                            'box': (
                                data['left'][i],
                                data['top'][i],
                                data['left'][i] + data['width'][i],
                                data['top'][i] + data['height'][i]
                            )
                        })
            
            # Calcula confiança média
            avg_conf = (total_conf / count) / 100 if count > 0 else 0
            
            return {
                'text': ' '.join(text_parts),
                'confidence': avg_conf,
                'boxes': valid_boxes
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            raise
    
    @property
    def name(self) -> str:
        return "Tesseract"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    @property
    def language_support(self) -> Dict[str, bool]:
        return self._languages.copy() 
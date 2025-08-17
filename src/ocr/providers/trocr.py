from pathlib import Path
from typing import Dict, Any
import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from ..base import OCRProvider
from ...utils.logger import get_logger
from ...utils.cache import cached

logger = get_logger(__name__)

class TrOCRProvider(OCRProvider):
    """Provider que usa TrOCR da HuggingFace"""
    
    def __init__(self):
        try:
            # Carrega modelo e processador
            self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
            self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
            
            # Move para GPU se disponível
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            
            self._available = True
        except Exception as e:
            logger.error(f"Erro ao inicializar TrOCR: {e}")
            self._available = False
    
    @cached("trocr_ocr")
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """Extrai texto usando TrOCR"""
        if not self.is_available:
            raise RuntimeError("TrOCR não está disponível")
        
        try:
            # Carrega e processa imagem
            image = Image.open(image_path).convert("RGB")
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)
            
            # Gera texto
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]
            
            # TrOCR não fornece confiança, usamos um valor fixo
            return {
                'text': generated_text.strip(),
                'confidence': 0.85,  # Valor estimado
                'boxes': []  # TrOCR não fornece bounding boxes
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            raise
    
    @property
    def name(self) -> str:
        return "TrOCR"
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    @property
    def language_support(self) -> Dict[str, bool]:
        # TrOCR base é treinado principalmente em inglês
        return {
            "eng": True,
            "por": False,
            "jpn": False
        } 
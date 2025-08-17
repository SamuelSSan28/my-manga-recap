from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class OCRProvider(ABC):
    """Interface base para provedores de OCR"""
    
    @abstractmethod
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """
        Extrai texto de uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dict contendo:
                - text: Texto extraído
                - confidence: Confiança da extração (0-1)
                - boxes: Lista de bounding boxes (opcional)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provider"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provider está disponível"""
        pass
    
    @property
    @abstractmethod
    def language_support(self) -> Dict[str, bool]:
        """
        Retorna dicionário de idiomas suportados
        Ex: {"por": True, "eng": True, "jpn": False}
        """
        pass 
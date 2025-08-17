from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path

class AIProvider(ABC):
    """Interface base para provedores de IA"""
    
    @abstractmethod
    def generate_script(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Gera um roteiro narrativo a partir do texto extraído.
        
        Args:
            text: Texto extraído da imagem
            context: Contexto adicional opcional (personagens, cena anterior, etc)
            
        Returns:
            str: Roteiro narrativo gerado
        """
        pass
    
    @abstractmethod
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """
        Gera áudio a partir do texto usando TTS.
        
        Args:
            text: Texto para converter em áudio
            output_path: Caminho para salvar o arquivo de áudio
            
        Returns:
            Path: Caminho do arquivo de áudio gerado
        """
        pass
    
    @abstractmethod
    def extract_text(self, image_path: Path) -> Dict[str, Any]:
        """
        Extrai texto e informações contextuais da imagem.
        
        Args:
            image_path: Caminho da imagem para processar
            
        Returns:
            Dict[str, Any]: Dicionário contendo texto e metadados extraídos
        """
        pass
    
    @abstractmethod
    def analyze_scene(self, image_path: Path, text: str) -> Dict[str, Any]:
        """
        Analisa a cena para extrair informações contextuais.
        
        Args:
            image_path: Caminho da imagem
            text: Texto extraído da imagem
            
        Returns:
            Dict[str, Any]: Informações da cena (personagens, ações, etc)
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
        """Verifica se o provider está disponível para uso"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Lista de recursos suportados pelo provider"""
        pass 
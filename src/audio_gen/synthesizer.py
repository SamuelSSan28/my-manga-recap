from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from pydub import AudioSegment

from ..ai_provider.base import AIProvider
from ..utils.logger import get_logger
from ..utils.cache import cached
from ..config.settings import AUDIO_SETTINGS

logger = get_logger(__name__)

class AudioSynthesizer:
    """Sintetizador de áudio para narração"""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self._settings = AUDIO_SETTINGS
    
    @cached("audio_scene")
    def synthesize_scene(
        self,
        text: str,
        output_path: Optional[Path] = None,
        add_silence: bool = True
    ) -> Path:
        """
        Sintetiza áudio para uma cena.
        
        Args:
            text: Texto para sintetizar
            output_path: Caminho opcional para salvar
            add_silence: Se deve adicionar silêncio no início/fim
            
        Returns:
            Path: Caminho do arquivo de áudio
        """
        try:
            # Define output_path se não fornecido
            if output_path is None:
                output_path = Path("temp") / "audio" / f"scene_{hash(text)}.{self._settings['format']}"
            
            # Gera áudio
            audio_path = self.provider.generate_audio(text, output_path)
            
            # Adiciona silêncio se necessário
            if add_silence:
                audio = AudioSegment.from_file(audio_path)
                
                # Adiciona 0.5s de silêncio no início e fim
                silence = AudioSegment.silent(duration=500)
                audio = silence + audio + silence
                
                # Salva resultado
                audio.export(
                    audio_path,
                    format=self._settings["format"],
                    parameters=[
                        "-ar", str(self._settings["sample_rate"]),
                        "-ac", str(self._settings["channels"])
                    ]
                )
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Erro ao sintetizar áudio: {e}")
            raise
    
    @cached("audio_chapter")
    def synthesize_chapter(
        self,
        script_data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Sintetiza áudio para um capítulo inteiro.
        
        Args:
            script_data: Dados do roteiro do capítulo
            output_path: Caminho opcional para salvar
            
        Returns:
            Path: Caminho do arquivo de áudio
        """
        try:
            # Define output_path se não fornecido
            if output_path is None:
                chapter_info = script_data.get("chapter_info", {})
                chapter_num = chapter_info.get("number", "unknown")
                output_path = Path("temp") / "audio" / f"chapter_{chapter_num}.{self._settings['format']}"
            
            # Cria diretório se necessário
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Processa cada cena
            scene_audios = []
            for scene_script in script_data["scenes"]:
                # Gera áudio da cena
                scene_path = self.synthesize_scene(scene_script)
                scene_audio = AudioSegment.from_file(scene_path)
                scene_audios.append(scene_audio)
            
            # Junta todos os áudios
            silence = AudioSegment.silent(duration=1000)  # 1s entre cenas
            chapter_audio = scene_audios[0]
            
            for scene_audio in scene_audios[1:]:
                chapter_audio = chapter_audio + silence + scene_audio
            
            # Salva resultado
            chapter_audio.export(
                output_path,
                format=self._settings["format"],
                parameters=[
                    "-ar", str(self._settings["sample_rate"]),
                    "-ac", str(self._settings["channels"])
                ]
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao sintetizar capítulo: {e}")
            raise
    
    def save_metadata(self, audio_path: Path, metadata: Dict[str, Any]) -> None:
        """
        Salva metadados do áudio.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            metadata: Metadados para salvar
        """
        try:
            metadata_path = audio_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {e}")
            raise
    
    def load_metadata(self, audio_path: Path) -> Dict[str, Any]:
        """
        Carrega metadados do áudio.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            Dict: Metadados do áudio
        """
        try:
            metadata_path = audio_path.with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar metadados: {e}")
            raise 
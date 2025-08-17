from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    TextClip, ColorClip, concatenate_videoclips
)

from ..utils.logger import get_logger
from ..utils.cache import cached
from ..config.settings import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT, DEFAULT_FPS

logger = get_logger(__name__)

class VideoComposer:
    """Compositor de vídeo para mangá narrado"""
    
    def __init__(
        self,
        width: int = DEFAULT_VIDEO_WIDTH,
        height: int = DEFAULT_VIDEO_HEIGHT,
        fps: int = DEFAULT_FPS
    ):
        self.width = width
        self.height = height
        self.fps = fps
    
    def _create_title_clip(
        self,
        text: str,
        duration: float = 3.0,
        font_size: int = 50,
        bg_color: str = 'black',
        font_color: str = 'white'
    ) -> CompositeVideoClip:
        """Cria clip de título"""
        # Cria fundo
        bg_clip = ColorClip(
            size=(self.width, self.height),
            color=bg_color,
            duration=duration
        )
        
        # Cria texto
        text_clip = TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            bg_color=None,
            size=(self.width * 0.8, None),
            method='caption'
        ).set_duration(duration)
        
        # Centraliza texto
        text_clip = text_clip.set_position('center')
        
        return CompositeVideoClip([bg_clip, text_clip])
    
    def _create_scene_clip(
        self,
        image_path: Path,
        audio_path: Path,
        fade_duration: float = 0.5
    ) -> CompositeVideoClip:
        """Cria clip de uma cena"""
        # Carrega áudio e pega duração
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration
        
        # Cria clip da imagem
        image = ImageClip(str(image_path))
        image = image.set_duration(duration)
        
        # Aplica fade in/out
        if fade_duration > 0:
            image = image.fadein(fade_duration).fadeout(fade_duration)
        
        # Adiciona áudio
        video = image.set_audio(audio)
        
        return video
    
    @cached("video_chapter")
    def create_chapter_video(
        self,
        chapter_data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Cria vídeo para um capítulo.
        
        Args:
            chapter_data: Dados do capítulo (imagens, áudios, etc)
            output_path: Caminho opcional para salvar
            
        Returns:
            Path: Caminho do vídeo gerado
        """
        try:
            # Define output_path se não fornecido
            if output_path is None:
                chapter_info = chapter_data.get("chapter_info", {})
                chapter_num = chapter_info.get("number", "unknown")
                output_path = Path("temp") / "video" / f"chapter_{chapter_num}.mp4"
            
            # Cria diretório se necessário
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Lista de clips para juntar
            clips = []
            
            # Adiciona título do capítulo
            chapter_info = chapter_data.get("chapter_info", {})
            title = f"Capítulo {chapter_info.get('number', '?')}: {chapter_info.get('title', 'Sem título')}"
            clips.append(self._create_title_clip(title))
            
            # Processa cada cena
            for scene in chapter_data["scenes"]:
                scene_clip = self._create_scene_clip(
                    image_path=scene["image_path"],
                    audio_path=scene["audio_path"]
                )
                clips.append(scene_clip)
            
            # Adiciona créditos finais
            clips.append(self._create_title_clip(
                "Fim do Capítulo",
                duration=2.0,
                font_size=40
            ))
            
            # Junta todos os clips
            final_video = concatenate_videoclips(clips)
            
            # Renderiza vídeo
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                threads=4
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao criar vídeo: {e}")
            raise
    
    def save_metadata(self, video_path: Path, metadata: Dict[str, Any]) -> None:
        """
        Salva metadados do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            metadata: Metadados para salvar
        """
        try:
            metadata_path = video_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {e}")
            raise
    
    def load_metadata(self, video_path: Path) -> Dict[str, Any]:
        """
        Carrega metadados do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Dict: Metadados do vídeo
        """
        try:
            metadata_path = video_path.with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar metadados: {e}")
            raise 
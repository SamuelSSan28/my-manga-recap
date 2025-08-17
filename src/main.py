import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from .config.settings import (
    DEFAULT_VIDEO_WIDTH,
    DEFAULT_VIDEO_HEIGHT,
    DEFAULT_FPS,
    DEFAULT_LANGUAGE
)
from .ai_provider.providers.openai import OpenAIProvider
from .ai_provider.providers.local import LocalProvider
from .ai_provider.providers.silent import SilentProvider
from .ocr.providers.tesseract import TesseractProvider
from .ocr.providers.trocr import TrOCRProvider
from .image_processor.enhancer import ImageEnhancer
from .script_gen.generator import ScriptGenerator
from .audio_gen.synthesizer import AudioSynthesizer
from .video_gen.composer import VideoComposer
from .utils.logger import get_logger

logger = get_logger(__name__)

class MangaRecap:
    """Classe principal que coordena o processo de geração"""
    
    def __init__(self):
        # Inicializa providers
        self.providers = {
            "openai": OpenAIProvider(),
            "local": LocalProvider(),
            "silent": SilentProvider()
        }
        
        # Seleciona melhor provider disponível
        self.provider = self._select_best_provider()
        
        # Inicializa componentes
        self.ocr = self._select_best_ocr()
        self.enhancer = ImageEnhancer()
        self.script_gen = ScriptGenerator(self.provider)
        self.audio_gen = AudioSynthesizer(self.provider)
        self.video_gen = VideoComposer()
    
    def _select_best_provider(self) -> Any:
        """Seleciona melhor provider disponível"""
        for name in ["openai", "local", "silent"]:
            provider = self.providers[name]
            if provider.is_available:
                logger.info(f"Usando provider: {name}")
                return provider
        return self.providers["silent"]
    
    def _select_best_ocr(self) -> Any:
        """Seleciona melhor OCR disponível"""
        # Tenta TrOCR primeiro
        try:
            trocr = TrOCRProvider()
            if trocr.is_available:
                logger.info("Usando TrOCR")
                return trocr
        except Exception as e:
            logger.warning(f"TrOCR não disponível: {e}")
        
        # Fallback para Tesseract
        return TesseractProvider()
    
    def process_chapter(
        self,
        chapter_dir: Path,
        output_path: Optional[Path] = None,
        chapter_info: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Processa um capítulo completo.
        
        Args:
            chapter_dir: Diretório com imagens do capítulo
            output_path: Caminho opcional para vídeo final
            chapter_info: Informações do capítulo
            
        Returns:
            Path: Caminho do vídeo gerado
        """
        try:
            logger.info(f"Processando capítulo: {chapter_dir}")
            
            # Lista imagens do capítulo
            images = sorted(
                [f for f in chapter_dir.glob("*") if f.suffix.lower() in {".jpg", ".jpeg", ".png"}]
            )
            
            if not images:
                raise ValueError(f"Nenhuma imagem encontrada em: {chapter_dir}")
            
            # Processa cada imagem
            scenes = []
            for img_path in images:
                logger.info(f"Processando imagem: {img_path}")
                
                # Melhora imagem para OCR
                enhanced_path = self.enhancer.enhance_for_ocr(img_path)
                
                # Extrai texto
                ocr_result = self.ocr.extract_text(enhanced_path)
                
                # Prepara imagem para vídeo
                video_path = self.enhancer.prepare_for_video(
                    img_path,
                    target_size=(DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT)
                )
                
                scenes.append({
                    "image_path": video_path,
                    "text": ocr_result["text"],
                    "confidence": ocr_result["confidence"]
                })
            
            # Gera roteiro
            script_data = self.script_gen.generate_chapter_script(
                scenes=scenes,
                chapter_info=chapter_info
            )
            
            # Gera áudio para cada cena
            for i, (scene, scene_script) in enumerate(zip(scenes, script_data["scenes"])):
                audio_path = self.audio_gen.synthesize_scene(scene_script)
                scenes[i]["audio_path"] = audio_path
            
            # Gera vídeo final
            chapter_data = {
                "scenes": scenes,
                "chapter_info": chapter_info
            }
            
            video_path = self.video_gen.create_chapter_video(
                chapter_data=chapter_data,
                output_path=output_path
            )
            
            logger.info(f"Vídeo gerado: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Erro ao processar capítulo: {e}")
            raise

def main():
    """Função principal da CLI"""
    parser = argparse.ArgumentParser(description="Converte mangás em vídeos narrados")
    
    parser.add_argument(
        "--chapters_dir",
        type=str,
        required=True,
        help="Diretório com os capítulos"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Arquivo de vídeo de saída"
    )
    
    parser.add_argument(
        "--max-chapters",
        type=int,
        help="Limite de capítulos (para teste)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignora checkpoints"
    )
    
    parser.add_argument(
        "--temp",
        type=str,
        default="temp",
        help="Diretório temporário"
    )
    
    parser.add_argument(
        "--lang",
        type=str,
        default=DEFAULT_LANGUAGE,
        help="Idioma da narração"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_VIDEO_WIDTH,
        help="Largura do vídeo"
    )
    
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_VIDEO_HEIGHT,
        help="Altura do vídeo"
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializa sistema
        manga_recap = MangaRecap()
        
        # Lista capítulos
        chapters_dir = Path(args.chapters_dir)
        chapters = sorted([d for d in chapters_dir.iterdir() if d.is_dir()])
        
        if args.max_chapters:
            chapters = chapters[:args.max_chapters]
        
        if not chapters:
            raise ValueError(f"Nenhum capítulo encontrado em: {chapters_dir}")
        
        # Processa cada capítulo
        for chapter_dir in chapters:
            try:
                # Extrai número do capítulo do nome do diretório
                chapter_num = chapter_dir.name
                
                chapter_info = {
                    "number": chapter_num,
                    "title": f"Capítulo {chapter_num}"
                }
                
                # Define caminho de saída
                if len(chapters) == 1:
                    output_path = Path(args.output)
                else:
                    output_dir = Path(args.output).parent
                    output_name = f"{Path(args.output).stem}_{chapter_num}{Path(args.output).suffix}"
                    output_path = output_dir / output_name
                
                # Processa capítulo
                manga_recap.process_chapter(
                    chapter_dir=chapter_dir,
                    output_path=output_path,
                    chapter_info=chapter_info
                )
                
            except Exception as e:
                logger.error(f"Erro ao processar capítulo {chapter_dir}: {e}")
                if not args.force:
                    raise
        
        logger.info("Processamento concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise

if __name__ == "__main__":
    main() 
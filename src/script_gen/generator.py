from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ..ai_provider.base import AIProvider
from ..utils.logger import get_logger
from ..utils.cache import cached

logger = get_logger(__name__)

class ScriptGenerator:
    """Gerador de roteiros para narração"""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
    
    def _load_template(self, template_name: str) -> str:
        """Carrega template de roteiro"""
        template_path = Path(__file__).parent / "templates" / f"{template_name}.txt"
        if template_path.exists():
            return template_path.read_text()
        return ""
    
    @cached("script_gen")
    def generate_scene_script(
        self,
        text: str,
        image_path: Optional[Path] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera roteiro para uma cena.
        
        Args:
            text: Texto extraído da cena
            image_path: Caminho opcional da imagem
            context: Contexto adicional
            
        Returns:
            Dict contendo roteiro e metadados
        """
        try:
            # Analisa cena se imagem fornecida
            scene_context = {}
            if image_path:
                scene_analysis = self.provider.analyze_scene(image_path, text)
                scene_context = scene_analysis.get("analysis", {})
            
            # Combina contextos
            full_context = {
                **(context or {}),
                **scene_context
            }
            
            # Gera roteiro
            script = self.provider.generate_script(text, full_context)
            
            return {
                "script": script,
                "context": full_context,
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar roteiro: {e}")
            raise
    
    @cached("chapter_script")
    def generate_chapter_script(
        self,
        scenes: List[Dict[str, Any]],
        chapter_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gera roteiro completo para um capítulo.
        
        Args:
            scenes: Lista de cenas com texto e contexto
            chapter_info: Informações do capítulo
            
        Returns:
            Dict contendo roteiro completo e metadados
        """
        try:
            chapter_info = chapter_info or {}
            
            # Template para juntar cenas
            template = self._load_template("chapter") or """
Capítulo {chapter_number}: {chapter_title}

{scenes}

Fim do capítulo {chapter_number}.
""".strip()
            
            # Processa cada cena
            processed_scenes = []
            previous_context = {}
            
            for scene in scenes:
                # Adiciona contexto da cena anterior
                scene_context = {
                    **(scene.get("context", {})),
                    "previous_scene": previous_context
                }
                
                # Gera roteiro da cena
                scene_script = self.generate_scene_script(
                    text=scene["text"],
                    image_path=scene.get("image_path"),
                    context=scene_context
                )
                
                processed_scenes.append(scene_script["script"])
                previous_context = scene_script["context"]
            
            # Monta roteiro completo
            full_script = template.format(
                chapter_number=chapter_info.get("number", "?"),
                chapter_title=chapter_info.get("title", "Sem título"),
                scenes="\n\n".join(processed_scenes)
            )
            
            return {
                "script": full_script,
                "scenes": processed_scenes,
                "chapter_info": chapter_info
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar roteiro do capítulo: {e}")
            raise
    
    def save_script(self, script_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Salva roteiro e metadados em arquivo JSON.
        
        Args:
            script_data: Dados do roteiro
            output_path: Caminho para salvar
            
        Returns:
            Path: Caminho do arquivo salvo
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            return output_path
        except Exception as e:
            logger.error(f"Erro ao salvar roteiro: {e}")
            raise
    
    def load_script(self, script_path: Path) -> Dict[str, Any]:
        """
        Carrega roteiro de arquivo JSON.
        
        Args:
            script_path: Caminho do arquivo
            
        Returns:
            Dict: Dados do roteiro
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar roteiro: {e}")
            raise 
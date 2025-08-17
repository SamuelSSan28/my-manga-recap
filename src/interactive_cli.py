import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import inquirer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .main import MangaRecap
from .utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

class InteractiveCLI:
    """Interface interativa para o MangaRecap"""
    
    def __init__(self):
        self.manga_recap = MangaRecap()
    
    def _select_directory(self, message: str, default: Optional[str] = None) -> Path:
        """Solicita seleção de diretório"""
        questions = [
            inquirer.Path(
                'path',
                message=message,
                path_type=inquirer.Path.DIRECTORY,
                default=default,
                exists=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        return Path(answers['path'])
    
    def _select_output(self, message: str, default: Optional[str] = None) -> Path:
        """Solicita caminho de saída"""
        questions = [
            inquirer.Path(
                'path',
                message=message,
                default=default
            )
        ]
        
        answers = inquirer.prompt(questions)
        return Path(answers['path'])
    
    def _confirm(self, message: str) -> bool:
        """Solicita confirmação"""
        questions = [
            inquirer.Confirm(
                'confirm',
                message=message,
                default=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['confirm']
    
    def _select_options(self) -> Dict[str, Any]:
        """Solicita opções de processamento"""
        questions = [
            inquirer.Text(
                'max_chapters',
                message="Número máximo de capítulos (vazio para todos)",
                default=""
            ),
            inquirer.Confirm(
                'force',
                message="Ignorar erros e continuar processamento?",
                default=False
            ),
            inquirer.List(
                'quality',
                message="Qualidade do vídeo",
                choices=[
                    ('HD (1280x720)', (1280, 720)),
                    ('Full HD (1920x1080)', (1920, 1080)),
                    ('4K (3840x2160)', (3840, 2160))
                ],
                default=(1280, 720)
            )
        ]
        
        return inquirer.prompt(questions)
    
    def run(self):
        """Executa interface interativa"""
        try:
            # Banner
            console.print("""
[bold cyan]🎬 My Manga Recap[/bold cyan]
Sistema para converter mangás em vídeos narrados
""")
            
            # Seleciona diretório de entrada
            chapters_dir = self._select_directory(
                "Selecione o diretório com os capítulos:",
                default="."
            )
            
            # Seleciona arquivo de saída
            output_path = self._select_output(
                "Nome do arquivo de vídeo de saída:",
                default="output.mp4"
            )
            
            # Opções adicionais
            options = self._select_options()
            
            # Confirma processamento
            if not self._confirm("Iniciar processamento?"):
                console.print("[yellow]Operação cancelada pelo usuário[/yellow]")
                return
            
            # Processa capítulos
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Lista capítulos
                chapters = sorted([d for d in chapters_dir.iterdir() if d.is_dir()])
                
                if options['max_chapters']:
                    try:
                        max_chapters = int(options['max_chapters'])
                        chapters = chapters[:max_chapters]
                    except ValueError:
                        pass
                
                if not chapters:
                    raise ValueError(f"Nenhum capítulo encontrado em: {chapters_dir}")
                
                # Processa cada capítulo
                for chapter_dir in chapters:
                    try:
                        # Atualiza progresso
                        task = progress.add_task(
                            f"Processando capítulo: {chapter_dir.name}",
                            total=None
                        )
                        
                        # Extrai número do capítulo
                        chapter_num = chapter_dir.name
                        
                        chapter_info = {
                            "number": chapter_num,
                            "title": f"Capítulo {chapter_num}"
                        }
                        
                        # Define caminho de saída
                        if len(chapters) == 1:
                            chapter_output = output_path
                        else:
                            output_dir = output_path.parent
                            output_name = f"{output_path.stem}_{chapter_num}{output_path.suffix}"
                            chapter_output = output_dir / output_name
                        
                        # Processa capítulo
                        self.manga_recap.process_chapter(
                            chapter_dir=chapter_dir,
                            output_path=chapter_output,
                            chapter_info=chapter_info
                        )
                        
                        # Marca como concluído
                        progress.remove_task(task)
                        console.print(f"[green]✓[/green] Capítulo {chapter_num} concluído")
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar capítulo {chapter_dir}: {e}")
                        progress.remove_task(task)
                        console.print(f"[red]✗[/red] Erro no capítulo {chapter_num}: {e}")
                        
                        if not options['force']:
                            raise
            
            console.print("\n[bold green]✨ Processamento concluído com sucesso![/bold green]")
            
        except Exception as e:
            logger.error(f"Erro fatal: {e}")
            console.print(f"\n[bold red]❌ Erro: {e}[/bold red]")
            sys.exit(1)

def main():
    """Função principal"""
    cli = InteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main() 
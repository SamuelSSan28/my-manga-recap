from pathlib import Path
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import time

from .logger import get_logger

logger = get_logger(__name__)

class BatchProcessor:
    """Processador em lote otimizado com filas e workers"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.task_queue = Queue(maxsize=queue_size)
        self.result_queue = Queue()
        self.workers = []
        self.running = False
    
    def add_task(self, task_id: str, task_func: Callable, *args, **kwargs):
        """Adiciona tarefa à fila"""
        task = {
            'id': task_id,
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }
        self.task_queue.put(task)
    
    def _worker(self):
        """Worker que processa tarefas da fila"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    self.result_queue.put({
                        'id': task['id'],
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    logger.error(f"Erro na tarefa {task['id']}: {e}")
                    self.result_queue.put({
                        'id': task['id'],
                        'error': str(e),
                        'success': False
                    })
                
                self.task_queue.task_done()
                
            except Exception:
                continue
    
    def start(self):
        """Inicia os workers"""
        self.running = True
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Para os workers"""
        self.running = False
        for _ in self.workers:
            self.task_queue.put(None)
        
        for worker in self.workers:
            worker.join()
    
    def process_batch(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa um lote de tarefas"""
        # Adiciona tarefas à fila
        for task in tasks:
            self.add_task(**task)
        
        # Coleta resultados
        results = {}
        while not self.task_queue.empty():
            result = self.result_queue.get()
            results[result['id']] = result
        
        return results

class OptimizedMangaProcessor:
    """Processador otimizado para mangá em lote"""
    
    def __init__(self, manga_recap):
        self.manga_recap = manga_recap
        self.batch_processor = BatchProcessor(max_workers=4)
    
    def process_chapters_batch(
        self,
        chapters: List[Path],
        output_dir: Path
    ) -> Dict[str, Path]:
        """Processa múltiplos capítulos em paralelo"""
        self.batch_processor.start()
        
        try:
            # Prepara tarefas
            tasks = []
            for chapter_dir in chapters:
                task = {
                    'task_id': chapter_dir.name,
                    'task_func': self._process_single_chapter,
                    'args': (chapter_dir, output_dir)
                }
                tasks.append(task)
            
            # Processa em lote
            results = self.batch_processor.process_batch(tasks)
            
            # Coleta resultados
            processed_chapters = {}
            for task_id, result in results.items():
                if result['success']:
                    processed_chapters[task_id] = result['result']
                else:
                    logger.error(f"Falha no capítulo {task_id}: {result['error']}")
            
            return processed_chapters
            
        finally:
            self.batch_processor.stop()
    
    def _process_single_chapter(self, chapter_dir: Path, output_dir: Path) -> Path:
        """Processa um único capítulo"""
        output_path = output_dir / f"{chapter_dir.name}.mp4"
        
        return self.manga_recap.process_chapter(
            chapter_dir=chapter_dir,
            output_path=output_path
        ) 
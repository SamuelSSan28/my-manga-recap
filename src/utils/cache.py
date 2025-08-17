import json
import time
from pathlib import Path
from typing import Any, Optional, Dict
from functools import wraps

from ..config.settings import CACHE_DIR, CACHE_ENABLED, CACHE_TTL
from .logger import get_logger

logger = get_logger(__name__)

class Cache:
    """Sistema de cache para resultados de operações"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Retorna o caminho do arquivo de cache para a chave"""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera um item do cache.
        
        Args:
            key: Chave do item
            
        Returns:
            Optional[Dict[str, Any]]: Item do cache ou None se não encontrado/expirado
        """
        if not CACHE_ENABLED:
            return None
            
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
            
        try:
            data = json.loads(cache_path.read_text())
            if time.time() - data["timestamp"] > CACHE_TTL:
                logger.debug(f"Cache expirado para chave: {key}")
                cache_path.unlink()
                return None
            return data["value"]
        except Exception as e:
            logger.error(f"Erro ao ler cache: {e}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Armazena um item no cache.
        
        Args:
            key: Chave do item
            value: Valor a ser armazenado
        """
        if not CACHE_ENABLED:
            return
            
        try:
            data = {
                "timestamp": time.time(),
                "value": value
            }
            cache_path = self._get_cache_path(key)
            cache_path.write_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Erro ao escrever cache: {e}")
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")

# Instância global do cache
cache = Cache()

def cached(key_prefix: str):
    """
    Decorator para cachear resultados de funções.
    
    Args:
        key_prefix: Prefixo para a chave do cache
        
    Returns:
        Callable: Decorator configurado
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
                
            # Gera uma chave única baseada nos argumentos
            key = f"{key_prefix}_{hash(str(args) + str(kwargs))}"
            
            # Tenta recuperar do cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit para {func.__name__}")
                return result
            
            # Executa a função e armazena no cache
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator 
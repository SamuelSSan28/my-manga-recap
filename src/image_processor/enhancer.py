from pathlib import Path
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from ..utils.logger import get_logger
from ..utils.cache import cached

logger = get_logger(__name__)

class ImageEnhancer:
    """Classe para melhorar qualidade de imagens para OCR"""
    
    @staticmethod
    def _resize_if_needed(image: Image.Image, max_size: int = 2048) -> Image.Image:
        """Redimensiona a imagem mantendo proporção se maior que max_size"""
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def _remove_noise(image: Image.Image, radius: int = 1) -> Image.Image:
        """Remove ruído usando filtro mediana"""
        return image.filter(ImageFilter.MedianFilter(radius))
    
    @staticmethod
    def _adjust_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Ajusta contraste da imagem"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def _adjust_sharpness(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Ajusta nitidez da imagem"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def _binarize(image: Image.Image, threshold: int = 128) -> Image.Image:
        """Converte para preto e branco usando threshold"""
        return image.convert('L').point(lambda x: 0 if x < threshold else 255, '1')
    
    @staticmethod
    def _auto_rotate(image: Image.Image) -> Tuple[Image.Image, float]:
        """
        Tenta detectar e corrigir rotação.
        Retorna imagem rotacionada e ângulo detectado.
        """
        try:
            # Converte para array numpy
            img_array = np.array(image.convert('L'))
            
            # Detecta linhas usando transformada de Hough
            from skimage.transform import hough_line, hough_line_peaks
            tested_angles = np.linspace(-np.pi / 4, np.pi / 4, 360)
            h, theta, d = hough_line(img_array, theta=tested_angles)
            
            # Encontra ângulo predominante
            _, angles, _ = hough_line_peaks(h, theta, d)
            angle = np.rad2deg(np.median(angles))
            
            # Rotaciona imagem
            rotated = image.rotate(angle, expand=True, fillcolor='white')
            return rotated, angle
        except Exception as e:
            logger.warning(f"Erro ao auto-rotacionar: {e}")
            return image, 0.0
    
    @staticmethod
    def _enhance_manga_specific(image: Image.Image) -> Image.Image:
        """Aplica técnicas específicas para mangá"""
        # Remove fundo branco
        image = image.convert('RGBA')
        data = image.getdata()
        
        new_data = []
        for item in data:
            # Se pixel é muito claro, torna transparente
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        return image
    
    @staticmethod
    def _apply_adaptive_threshold(image: Image.Image) -> Image.Image:
        """Aplica threshold adaptativo"""
        import cv2
        import numpy as np
        
        # Converte para OpenCV
        img_array = np.array(image.convert('L'))
        
        # Aplica threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return Image.fromarray(thresh)
    
    @cached("image_enhance")
    def enhance_for_ocr(
        self,
        image_path: Path,
        output_path: Optional[Path] = None,
        max_size: int = 2048,
        contrast_factor: float = 1.5,
        sharpness_factor: float = 1.5,
        denoise: bool = True,
        auto_rotate: bool = True,
        binarize: bool = True
    ) -> Path:
        """
        Melhora a imagem para OCR aplicando várias técnicas.
        
        Args:
            image_path: Caminho da imagem de entrada
            output_path: Caminho opcional para salvar resultado
            max_size: Tamanho máximo da imagem
            contrast_factor: Fator de ajuste de contraste
            sharpness_factor: Fator de ajuste de nitidez
            denoise: Se deve remover ruído
            auto_rotate: Se deve tentar corrigir rotação
            binarize: Se deve binarizar a imagem
            
        Returns:
            Path: Caminho da imagem processada
        """
        try:
            # Carrega imagem
            image = Image.open(image_path)
            
            # Define output_path se não fornecido
            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_enhanced{image_path.suffix}"
            
            # Redimensiona se necessário
            image = self._resize_if_needed(image, max_size)
            
            # Auto-rotação
            if auto_rotate:
                image, angle = self._auto_rotate(image)
                if abs(angle) > 0.5:
                    logger.info(f"Rotacionou imagem em {angle:.1f} graus")
            
            # Remove ruído
            if denoise:
                image = self._remove_noise(image)
            
            # Ajusta contraste
            image = self._adjust_contrast(image, contrast_factor)
            
            # Ajusta nitidez
            image = self._adjust_sharpness(image, sharpness_factor)
            
            # Binariza
            if binarize:
                image = self._binarize(image)
            
            # Salva resultado
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            raise
    
    @cached("image_prepare")
    def prepare_for_video(
        self,
        image_path: Path,
        output_path: Optional[Path] = None,
        target_size: Tuple[int, int] = (1280, 720),
        quality: int = 95
    ) -> Path:
        """
        Prepara imagem para uso em vídeo.
        
        Args:
            image_path: Caminho da imagem de entrada
            output_path: Caminho opcional para salvar resultado
            target_size: Tamanho alvo (width, height)
            quality: Qualidade da imagem de saída (1-100)
            
        Returns:
            Path: Caminho da imagem processada
        """
        try:
            # Carrega imagem
            image = Image.open(image_path)
            
            # Define output_path se não fornecido
            if output_path is None:
                output_path = image_path.parent / f"{image_path.stem}_video{image_path.suffix}"
            
            # Calcula novo tamanho mantendo proporção
            src_width, src_height = image.size
            src_ratio = src_width / src_height
            target_width, target_height = target_size
            target_ratio = target_width / target_height
            
            if src_ratio > target_ratio:
                # Imagem mais larga que o alvo
                new_width = target_width
                new_height = int(target_width / src_ratio)
            else:
                # Imagem mais alta que o alvo
                new_height = target_height
                new_width = int(target_height * src_ratio)
            
            # Redimensiona
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Cria imagem de fundo preta
            background = Image.new('RGB', target_size, (0, 0, 0))
            
            # Centraliza imagem
            offset_x = (target_width - new_width) // 2
            offset_y = (target_height - new_height) // 2
            background.paste(image, (offset_x, offset_y))
            
            # Salva resultado
            output_path.parent.mkdir(parents=True, exist_ok=True)
            background.save(output_path, quality=quality)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao preparar imagem para vídeo: {e}")
            raise 
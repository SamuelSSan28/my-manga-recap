import os
import json
from typing import List, Dict
from PIL import Image

from .ocr_provider import OCRManager

# Initialize default OCR manager with fallback providers
_ocr_manager = OCRManager()


def extract_text_from_image(image_path: str) -> str:
    """Extract text from a single image file using the OCR manager."""
    try:
        return _ocr_manager.extract_text(image_path)
    except Exception as exc:
        print(f"Failed to process {image_path}: {exc}")
        return f"[Erro ao processar: {exc}]"


def extract_text_from_chapter(chapter_dir: str, manager: OCRManager = _ocr_manager) -> Dict[str, any]:
    """Extract text from all images in a chapter directory with image-text linking."""
    chapter_name = os.path.basename(chapter_dir)
    image_files = [f for f in sorted(os.listdir(chapter_dir)) 
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    
    # Structure: chapter_name-page-XXX -> text
    page_data = {}
    texts_with_content = []
    
    print(f"📖 Processando {len(image_files)} páginas do capítulo {chapter_name}...")
    
    for i, file in enumerate(image_files, 1):
        path = os.path.join(chapter_dir, file)
        
        # Create unique key for this page
        page_key = f"{chapter_name}-page-{i:03d}"
        
        # Extract text from image
        text = manager.extract_text(path)
        
        # Store with metadata
        page_data[page_key] = {
            "image_file": file,
            "image_path": path,
            "page_number": i,
            "text": text,
            "has_content": text and not text.startswith("[")
        }
        
        # Collect texts with actual content for summary
        if page_data[page_key]["has_content"]:
            texts_with_content.append(text)
        
        # Show progress for larger chapters
        if len(image_files) > 10 and i % 5 == 0:
            print(f"   📄 Processadas {i}/{len(image_files)} páginas...")
    
    # Calculate statistics
    pages_with_content = sum(1 for p in page_data.values() if p["has_content"])
    
    return {
        "chapter_name": chapter_name,
        "chapter_dir": chapter_dir,
        "total_pages": len(image_files),
        "pages_with_content": pages_with_content,
        "page_data": page_data,  # Individual pages with linking
        "content_texts": texts_with_content,  # Only texts with content for script generation
        "has_meaningful_content": pages_with_content > 0
    }


def extract_text_from_chapter_simple(chapter_dir: str, manager: OCRManager = _ocr_manager) -> str:
    """Backward compatibility: Extract concatenated text from chapter directory."""
    result = extract_text_from_chapter(chapter_dir, manager)
    return "\n".join(result["content_texts"])

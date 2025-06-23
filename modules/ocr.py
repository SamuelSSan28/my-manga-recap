import os
from typing import List
from PIL import Image
import pytesseract

def extract_text_from_chapter(chapter_dir: str) -> str:
    """Extract concatenated text from all images in a chapter directory."""
    texts: List[str] = []
    for file in sorted(os.listdir(chapter_dir)):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            path = os.path.join(chapter_dir, file)
            try:
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
                texts.append(text)
            except Exception as exc:
                print(f"Failed to process {path}: {exc}")
    return "\n".join(texts)

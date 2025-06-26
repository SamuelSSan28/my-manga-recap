"""OCR provider system with fallback between Tesseract and TrOCR."""

from abc import ABC, abstractmethod
from typing import Optional, List

from PIL import Image
import pytesseract


class OCRProvider(ABC):
    """Base class for OCR providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if provider can be used."""

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from a PIL image."""


class TesseractProvider(OCRProvider):
    """Default OCR provider using pytesseract."""

    def is_available(self) -> bool:
        return True

    def extract_text(self, image: Image.Image) -> str:
        return pytesseract.image_to_string(image, lang="eng+por")


class TrOCRProvider(OCRProvider):
    """OCR using HuggingFace TrOCR (transformers)."""

    def __init__(self) -> None:
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            self.processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
            self.model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")
            self.model.eval()
            self._available = True
        except Exception as exc:  # pragma: no cover - optional dependency
            self._available = False
            self._error = str(exc)

    def is_available(self) -> bool:
        return getattr(self, "_available", False)

    def extract_text(self, image: Image.Image) -> str:
        if not self.is_available():
            raise RuntimeError(getattr(self, "_error", "TrOCR not available"))
        import torch  # torch is required for the model
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text.strip()


class OCRManager:
    """Manages multiple OCR providers with fallback."""

    def __init__(self, provider_name: Optional[str] = None) -> None:
        self.providers: List[OCRProvider] = []

        if provider_name in (None, "trocr"):
            try:
                trocr = TrOCRProvider()
                if trocr.is_available():
                    self.providers.append(trocr)
                else:
                    print(f"⚠️  TrOCR indisponível: {getattr(trocr, '_error', '')}")
            except Exception as exc:  # pragma: no cover - safety
                print(f"⚠️  Erro ao iniciar TrOCR: {exc}")

        # Always fall back to Tesseract
        self.providers.append(TesseractProvider())

    def extract_text(self, image_path: str) -> str:
        with Image.open(image_path) as img:
            for provider in self.providers:
                try:
                    text = provider.extract_text(img)
                    if text.strip():
                        return text.strip()
                except Exception as exc:
                    print(f"⚠️  {provider.__class__.__name__} falhou: {exc}")
        return "[Página vazia]"

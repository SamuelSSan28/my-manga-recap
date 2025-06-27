"""OCR provider system with fallback between Tesseract and TrOCR."""

from abc import ABC, abstractmethod
from typing import Optional, List

import base64
import io

from PIL import Image
import pytesseract

from .config import OPENAI_API_KEY, OPENAI_VISION_MODEL, DEFAULT_LANG


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


class OpenAIVisionProvider(OCRProvider):
    """OCR provider using OpenAI vision models with contextual extraction."""

    def __init__(self, model: Optional[str] = None, lang: str = DEFAULT_LANG) -> None:
        self.model = model or OPENAI_VISION_MODEL
        self.lang = lang

    def is_available(self) -> bool:
        if not OPENAI_API_KEY:
            return False
        try:
            import openai  # type: ignore
        except Exception:
            return False
        return True

    def extract_text(self, image: Image.Image) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI not configured")

        import openai  # type: ignore

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = (
            "Read the text from this manga page and identify any characters and "
            "context. Reply in {lang}."
        ).format(lang=self.lang)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ],
            }
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.get("content", "").strip()


class OCRManager:
    """Manages multiple OCR providers with fallback."""

    def __init__(self, provider_name: Optional[str] = None) -> None:
        self.providers: List[OCRProvider] = []

        if provider_name in (None, "openai"):
            try:
                openai_provider = OpenAIVisionProvider(lang=DEFAULT_LANG)
                if openai_provider.is_available():
                    self.providers.append(openai_provider)
                else:
                    print("⚠️  OpenAI Vision indisponível")
            except Exception as exc:  # pragma: no cover - safety
                print(f"⚠️  Erro ao iniciar OpenAI Vision: {exc}")

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

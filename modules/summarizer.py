from typing import List
from transformers import pipeline
from .config import DEFAULT_MODEL, DEFAULT_PROMPT


def summarize_text(
    chapter_texts: List[str],
    model: str = DEFAULT_MODEL,
    prompt: str | None = None,
    max_new_tokens: int = 256,
) -> List[str]:
    """Summarize a list of chapter texts using a customizable prompt."""

    if prompt is None:
        prompt = DEFAULT_PROMPT

    summarizer = pipeline("text2text-generation", model=model)

    summaries: List[str] = []
    for text in chapter_texts:
        if not text.strip():
            summaries.append("")
            continue
        try:
            full_prompt = f"{prompt}\n{text}"
            result = summarizer(full_prompt, max_new_tokens=max_new_tokens)
            summaries.append(result[0]["generated_text"])
        except Exception as exc:
            print(f"Failed to summarize text: {exc}")
            summaries.append("")
    return summaries

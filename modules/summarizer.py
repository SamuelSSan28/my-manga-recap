from typing import List
from transformers import pipeline


def summarize_text(
    chapter_texts: List[str],
    model: str = "google/flan-t5-base",
    prompt: str | None = None,
    max_new_tokens: int = 256,
) -> List[str]:
    """Summarize a list of chapter texts using a customizable prompt."""

    if prompt is None:
        prompt = (
            "Resuma o seguinte texto de forma narrativa. Utilize '[PAUSA]' para "
            "indicar pausas e sugira imagens no formato [IMAGEM: descricao]."
        )

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

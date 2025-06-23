from typing import List
from transformers import pipeline


def summarize_text(chapter_texts: List[str], model: str = "facebook/bart-large-cnn") -> List[str]:
    """Summarize a list of chapter texts."""
    summarizer = pipeline("summarization", model=model)
    summaries: List[str] = []
    for text in chapter_texts:
        if not text.strip():
            summaries.append("")
            continue
        try:
            summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as exc:
            print(f"Failed to summarize text: {exc}")
            summaries.append("")
    return summaries

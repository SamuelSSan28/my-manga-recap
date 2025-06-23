from typing import List


def build_script(chapter_summaries: List[str]) -> str:
    """Combine chapter summaries into a single narration script."""
    script_lines = []
    for i, summary in enumerate(chapter_summaries, 1):
        script_lines.append(f"Capítulo {i} resumo:\n{summary}\n")
    return "\n".join(script_lines)

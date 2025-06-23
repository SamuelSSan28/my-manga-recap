from typing import List


def build_script(chapter_summaries: List[str]) -> str:
    """Combine chapter summaries into a narrated script with tags."""

    script_lines = []
    for i, summary in enumerate(chapter_summaries, 1):
        script_lines.append(f"Capítulo {i}:")
        script_lines.append(summary)
        script_lines.append("")
    return "\n".join(script_lines)

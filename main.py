import argparse
import os
from modules.ocr import extract_text_from_chapter
from modules.summarizer import summarize_text
from modules.script_gen import build_script
from modules.audio_gen import text_to_speech
from modules.video_gen import create_video


def parse_args():
    parser = argparse.ArgumentParser(description="Generate video recap from manga chapters")
    parser.add_argument("--chapters_dir", required=True, help="Directory containing chapter folders with images")
    parser.add_argument("--output", required=True, help="Output video file")
    parser.add_argument("--lang", default="pt", help="Language for narration")
    parser.add_argument("--temp", default="temp", help="Temporary working directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.makedirs(args.temp, exist_ok=True)

    # Discover chapter directories
    chapter_dirs = [os.path.join(args.chapters_dir, d)
                    for d in sorted(os.listdir(args.chapters_dir))
                    if os.path.isdir(os.path.join(args.chapters_dir, d))]
    if not chapter_dirs:
        raise ValueError("No chapter directories found")

    # OCR text extraction
    chapter_texts = [extract_text_from_chapter(chapter) for chapter in chapter_dirs]

    # Summarization
    summaries = summarize_text(chapter_texts)

    # Build script
    script = build_script(summaries)
    script_path = os.path.join(args.temp, "script.txt")
    with open(script_path, "w") as f:
        f.write(script)

    # Generate audio narration
    audio_path = os.path.join(args.temp, "narration.mp3")
    text_to_speech(script, audio_path, lang=args.lang)

    # Generate video from images and narration
    create_video(chapter_dirs, audio_path, args.output)


if __name__ == "__main__":
    main()

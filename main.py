import argparse
import os
from modules.ocr import extract_text_from_chapter
from modules.summarizer import summarize_text
from modules.script_gen import build_script
from modules.audio_gen import text_to_speech
from modules.video_gen import create_video
from modules.config import (
    DEFAULT_TEMP_DIR,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    DEFAULT_IMAGE_DURATION,
    DEFAULT_USE_TTS,
    DEFAULT_VIDEO_WIDTH,
    DEFAULT_VIDEO_HEIGHT,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate video recap from manga chapters")
    parser.add_argument("--chapters_dir", required=True, help="Directory containing chapter folders with images")
    parser.add_argument("--output", required=True, help="Output video file")
    parser.add_argument("--lang", default=DEFAULT_LANG, help="Language for narration")
    parser.add_argument("--temp", default=DEFAULT_TEMP_DIR, help="Temporary working directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HuggingFace model for summarization")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Custom prompt for summarization")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice name for narration")
    parser.add_argument("--image_duration", type=float, default=DEFAULT_IMAGE_DURATION, help="Duration for each image in seconds")
    parser.add_argument("--use_tts", action="store_true", default=DEFAULT_USE_TTS, help="Use neural TTS if available")
    parser.add_argument("--width", type=int, default=DEFAULT_VIDEO_WIDTH, help="Output video width")
    parser.add_argument("--height", type=int, default=DEFAULT_VIDEO_HEIGHT, help="Output video height")
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
    summaries = summarize_text(chapter_texts, model=args.model, prompt=args.prompt)

    # Build script
    script = build_script(summaries)
    script_path = os.path.join(args.temp, "script.txt")
    with open(script_path, "w") as f:
        f.write(script)

    # Generate audio narration
    audio_path = os.path.join(args.temp, "narration.mp3")
    text_to_speech(
        script,
        audio_path,
        lang=args.lang,
        voice_name=args.voice,
        use_tts=args.use_tts,
    )

    # Generate video from images and narration
    create_video(
        chapter_dirs,
        audio_path,
        args.output,
        script=script,
        image_duration=args.image_duration,
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    main()

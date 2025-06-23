import os
from typing import List
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def create_video(chapter_dirs: List[str], audio_path: str, output_path: str) -> None:
    """Create a simple video using images from chapters and an audio narration."""
    clips = []
    for chapter in chapter_dirs:
        for file in sorted(os.listdir(chapter)):
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                img_path = os.path.join(chapter, file)
                clip = ImageClip(img_path).set_duration(2)
                clips.append(clip)
    if not clips:
        raise ValueError("No images found for video generation")
    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    video.write_videofile(output_path, fps=24)

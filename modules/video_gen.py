import os
import re
from typing import List
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def create_video(
    chapter_dirs: List[str],
    audio_path: str,
    output_path: str,
    script: str,
    image_duration: float | None = None,
) -> None:
    """Create a video synchronizing narration audio with images."""

    all_images: List[str] = []
    for chapter in chapter_dirs:
        for file in sorted(os.listdir(chapter)):
            if file.lower().endswith((".png", "jpg", "jpeg", "webp")):
                img_path = os.path.join(chapter, file)
                all_images.append(img_path)

    tags = re.findall(r"\[IMAGEM[^\]]*\]", script)
    if not tags:
        raise ValueError("Script does not contain any [IMAGEM] tags")
    if len(tags) > len(all_images):
        raise ValueError("Not enough images for the tags in script")

    audio = AudioFileClip(audio_path)
    if image_duration is None:
        duration = audio.duration / len(tags)
    else:
        duration = image_duration

    clips = [ImageClip(all_images[i]).set_duration(duration) for i in range(len(tags))]

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    video.write_videofile(output_path, fps=24)

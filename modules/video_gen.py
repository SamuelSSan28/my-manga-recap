import os
import re
from typing import List
import numpy as np
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips


def create_video(
    chapter_dirs: List[str],
    audio_path: str,
    output_path: str,
    script: str,
    image_duration: float | None = None,
    width: int = 1280,
    height: int = 720,
) -> None:
    """Create a video synchronizing narration audio with images.

    Images are cropped to fit the desired ``width``/``height`` aspect ratio so
    that long manga pages better fit a standard video format.
    """

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

    def _prepare_clip(path: str) -> ImageClip:
        """Load image, crop to desired aspect ratio and resize."""
        img = Image.open(path)
        target_ratio = width / height
        img_ratio = img.width / img.height

        if img_ratio < target_ratio:
            # Image too tall: crop vertically
            new_height = int(img.width / target_ratio)
            top = max((img.height - new_height) // 2, 0)
            img = img.crop((0, top, img.width, top + new_height))
        elif img_ratio > target_ratio:
            # Image too wide: crop horizontally
            new_width = int(img.height * target_ratio)
            left = max((img.width - new_width) // 2, 0)
            img = img.crop((left, 0, left + new_width, img.height))

        img = img.resize((width, height))
        return ImageClip(np.array(img)).set_duration(duration)

    clips = [_prepare_clip(all_images[i]) for i in range(len(tags))]

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)
    video.write_videofile(output_path, fps=24)

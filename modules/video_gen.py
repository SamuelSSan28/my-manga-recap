import os
import re
import json
from typing import List, Optional, Dict, Any
import numpy as np
from PIL import Image
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


def _calculate_text_timing(script: str, total_duration: float) -> List[float]:
    """Calculate timing for each text segment based on pauses and content length."""
    lines = script.split('\n')
    segments = []
    current_text = ""
    
    for line in lines:
        line = line.strip()
        if line.startswith('[PAUSA'):
            if current_text:
                segments.append(current_text)
                current_text = ""
        elif line and not line.startswith('['):
            current_text += " " + line
    
    # Add final segment
    if current_text:
        segments.append(current_text)
    
    if not segments:
        return []
    
    # Calculate duration for each segment based on text length
    text_lengths = [len(seg.split()) for seg in segments]
    total_words = sum(text_lengths)
    
    if total_words == 0:
        return [total_duration / len(segments)] * len(segments)
    
    # Distribute time proportionally to text length
    timings = []
    for length in text_lengths:
        timing = (length / total_words) * total_duration
        timings.append(max(timing, 0.5))  # Minimum 0.5s per segment
    
    return timings


def _load_ocr_data(temp_dir: str) -> Optional[List[Dict[str, Any]]]:
    """Load OCR data to get image-text associations."""
    ocr_file = os.path.join(temp_dir, "chapter_texts.json")
    if os.path.exists(ocr_file):
        try:
            with open(ocr_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None


def create_video(
    chapter_dirs: List[str],
    audio_path: str,
    output_path: str,
    script: str,
    image_duration: Optional[float] = None,
    width: int = 1280,
    height: int = 720,
    temp_dir: str = "temp",
) -> None:
    """Create a video with intelligent image-text synchronization."""

    # Try to load OCR data for intelligent sync
    ocr_data = _load_ocr_data(temp_dir)
    
    # Collect all images from chapters, filtering out empty pages
    all_images: List[str] = []
    image_to_text = {}  # Map image path to its text content
    
    for chapter in chapter_dirs:
        chapter_name = os.path.basename(chapter)
        for file in sorted(os.listdir(chapter)):
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                img_path = os.path.join(chapter, file)
                
                # Try to find corresponding text from OCR data
                page_text = ""
                has_content = False
                
                if ocr_data:
                    for ch_data in ocr_data:
                        if ch_data["chapter_name"] == chapter_name:
                            page_data = ch_data.get("page_data", {})
                            for page_key, page_info in page_data.items():
                                if page_info["image_file"] == file:
                                    page_text = page_info.get("text", "")
                                    has_content = page_info.get("has_content", False)
                                    break
                
                # Only include pages with actual content (ignore empty pages)
                if has_content and page_text and not page_text.startswith("[Página vazia]") and not page_text.startswith("[Erro ao processar"):
                    all_images.append(img_path)
                    image_to_text[img_path] = page_text
                else:
                    print(f"   🚫 Ignorando página vazia/erro: {file}")

    if not all_images:
        raise ValueError("No images with content found in chapter directories")

    print(f"🖼️  Selecionadas {len(all_images)} imagens com conteúdo para o vídeo")
    
    # Load audio to get duration
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    print(f"🎵 Duração do áudio: {total_duration:.2f}s")

    # Calculate timing strategy - always follow the audio duration
    if image_duration is not None:
        # Fixed duration mode - but still respect total audio duration
        total_calculated = image_duration * len(all_images)
        if total_calculated > total_duration:
            # Adjust to fit audio duration
            adjusted_duration = total_duration / len(all_images)
            print(f"⚠️  Ajustando duração fixa de {image_duration:.2f}s para {adjusted_duration:.2f}s (para caber no áudio)")
            timings = [adjusted_duration] * len(all_images)
        else:
            timings = [image_duration] * len(all_images)
            print(f"⏱️  Modo fixo: {image_duration:.2f}s por imagem")
    else:
        # Intelligent timing based on script segments
        text_timings = _calculate_text_timing(script, total_duration)
        
        if text_timings and len(text_timings) > 0:
            print(f"🧠 Modo inteligente: {len(text_timings)} segmentos de texto")
            
            # Map images to text segments based on their content
            images_per_segment = len(all_images) // len(text_timings)
            remainder = len(all_images) % len(text_timings)
            
            timings = []
            
            for i, segment_duration in enumerate(text_timings):
                # Number of images for this segment
                num_images = images_per_segment + (1 if i < remainder else 0)
                
                if num_images > 0:
                    img_duration = segment_duration / num_images
                    for _ in range(num_images):
                        timings.append(img_duration)
            
            print(f"📊 Timings calculados para {len(timings)} imagens com conteúdo")
        else:
            # Fallback to uniform distribution
            duration_per_image = total_duration / len(all_images)
            timings = [duration_per_image] * len(all_images)
            print(f"⚠️  Fallback: distribuição uniforme ({duration_per_image:.2f}s)")

    def _prepare_clip(path: str, duration: float) -> ImageClip:
        """Load image, crop to desired aspect ratio and resize."""
        try:
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
            return ImageClip(np.array(img)).with_duration(duration)
        
        except Exception as e:
            print(f"⚠️  Erro ao processar {path}: {e}")
            # Create a black frame as fallback
            black_frame = np.zeros((height, width, 3), dtype=np.uint8)
            return ImageClip(black_frame).with_duration(duration)

    # Create clips with calculated timings
    print("🎬 Criando clipes de vídeo...")
    clips = []
    cumulative_time = 0
    
    for i, (img_path, timing) in enumerate(zip(all_images, timings)):
        if i % 10 == 0:
            print(f"   📽️  Processando {i+1}/{len(all_images)} imagens com conteúdo...")
        
        clip = _prepare_clip(img_path, timing)
        clips.append(clip)
        cumulative_time += timing
        
        # Show timing info for first few images
        if i < 5:
            text_preview = image_to_text.get(img_path, "")[:50] + "..." if image_to_text.get(img_path) else "[sem texto]"
            print(f"     🖼️  {os.path.basename(img_path)}: {timing:.2f}s - {text_preview}")

    print("🔗 Concatenando vídeo...")
    
    # Concatenate all clips
    video = concatenate_videoclips(clips, method="compose")
    
    # Ensure video matches audio duration exactly
    if abs(video.duration - audio.duration) > 0.1:  # Allow 0.1s tolerance
        print(f"⚖️  Ajustando duração final: vídeo {video.duration:.2f}s -> áudio {audio.duration:.2f}s")
        
        if video.duration > audio.duration:
            # Video longer than audio - trim
            video = video.subclipped(0, audio.duration)
        else:
            # Video shorter than audio - extend last clip
            extra_time = audio.duration - video.duration
            print(f"   ➕ Estendendo última imagem em {extra_time:.2f}s")
            last_clip = clips[-1].with_duration(clips[-1].duration + extra_time)
            clips[-1] = last_clip
            video = concatenate_videoclips(clips, method="compose")
    
    # Set audio
    video = video.with_audio(audio)
    
    print(f"💾 Salvando vídeo: {output_path}")
    video.write_videofile(output_path, fps=24, logger=None)
    
    print(f"✅ Vídeo criado com sucesso!")
    print(f"   📊 {len(all_images)} imagens com conteúdo, duração: {video.duration:.2f}s")
    print(f"   🎵 Sincronizado com áudio de {audio.duration:.2f}s")

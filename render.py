from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, vfx
)
import os
import math
from config import OUTPUT_DIR


def make_ken_burns(image_path, duration, width, height, zoom_in=True, intensity=0.15):
    """Slow zoom in/out on a single image for cinematic feel."""
    clip = ImageClip(image_path).set_duration(duration)
    # Oversize by intensity so zoom doesn't reveal edges
    clip = clip.resize(height=int(height * (1 + intensity)))

    def zoom_factor(t):
        progress = t / duration
        if zoom_in:
            return 1 + (intensity * progress)
        else:
            return (1 + intensity) - (intensity * progress)

    clip = clip.resize(lambda t: zoom_factor(t))
    clip = clip.set_position("center")
    return clip


def render_video(image_paths, audio_path, topic, is_short=False):
    print(f"🎬 Rendering video for {topic}...")

    if is_short:
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    n = max(len(image_paths), 1)
    per_image = total_duration / n

    print(f"📽️ {n} images × {per_image:.1f}s each = {total_duration:.1f}s total")

    clips = []
    for i, img in enumerate(image_paths):
        zoom_in = (i % 2 == 0)  # alternate in/out for variety
        clip = make_ken_burns(img, per_image, width, height, zoom_in=zoom_in)
        clips.append(clip)

    if not clips:
        clips = [ColorClip((width, height), color=(15, 15, 25), duration=total_duration)]

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in topic)[:60]
    suffix = "short" if is_short else "long"
    out = os.path.join(OUTPUT_DIR, f"{safe}_{suffix}.mp4")

    video.write_videofile(
        out, fps=24, codec="libx264", audio_codec="aac",
        preset="ultrafast", threads=2, logger=None
    )
    print(f"✅ Video saved: {out}")
    return out

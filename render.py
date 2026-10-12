from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import os
from config import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, SHORT_WIDTH, SHORT_HEIGHT

def render_video(bg_path, char_path, audio_path, topic, is_short=False):
    print(f"🎬 Rendering video for {topic}...")
    
    if is_short:
        width, height = SHORT_WIDTH, SHORT_HEIGHT
    else:
        width, height = VIDEO_WIDTH, VIDEO_HEIGHT
    
    # 1. Background Image (Zoom effect)
    bg_clip = ImageClip(bg_path).set_duration(AudioFileClip(audio_path).duration)
    bg_clip = bg_clip.resize(height=height).set_position("center")
    
    # 2. Character Image (Bouncing effect)
    char_clip = ImageClip(char_path).set_duration(bg_clip.duration)
    char_clip = char_clip.resize(height=height // 3) # Make character 1/3 of screen height
    # Center the character, slightly above bottom
    char_clip = char_clip.set_position(("center", height - char_clip.h - 100))
    
    # Add a simple bounce animation to the character
    def bounce(t):
        import math
        return 20 * math.sin(t * 10) # Move up and down by 20 pixels
    
    char_clip = char_clip.set_position(lambda t: ("center", height - char_clip.h - 100 + bounce(t)))
    
    # 3. Combine
    video = CompositeVideoClip([bg_clip, char_clip], size=(width, height))
    
    # 4. Add Audio
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)
    
    # 5. Export
    safe_topic = topic.replace(' ', '_').replace('/', '_')
    output_filename = f"{safe_topic}_{'short' if is_short else 'long'}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Use lower FPS to save processing time on free GitHub servers
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video saved: {output_path}")
    return output_path

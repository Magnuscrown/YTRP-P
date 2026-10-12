from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import os
from config import OUTPUT_DIR

def render_video(bg_path, char_path, audio_path, topic, is_short=False):
    print(f"🎬 Rendering video for {topic}...")
    
    if is_short:
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080
    
    # 1. Background Image (Scale to perfectly fill the frame)
    audio_clip = AudioFileClip(audio_path)
    bg_clip = ImageClip(bg_path).set_duration(audio_clip.duration)
    bg_clip = bg_clip.resize((width, height))  # Force exact dimensions
    
    # 2. Character Image (Bouncing effect)
    # Make character smaller for shorts so it doesn't block the whole screen
    char_height = height // 4 if not is_short else height // 5
    char_clip = ImageClip(char_path).set_duration(bg_clip.duration)
    char_clip = char_clip.resize(height=char_height)
    
    # Position character at the bottom center
    def bounce(t):
        import math
        return 15 * math.sin(t * 8)  # Move up and down by 15 pixels
    
    char_clip = char_clip.set_position(lambda t: ("center", height - char_clip.h - 80 + bounce(t)))
    
    # 3. Combine everything
    video = CompositeVideoClip([bg_clip, char_clip], size=(width, height))
    video = video.set_audio(audio_clip)
    
    # 4. Export
    safe_topic = topic.replace(' ', '_').replace('/', '_')
    output_filename = f"{safe_topic}_{'short' if is_short else 'long'}.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Use lower FPS to save processing time on free GitHub servers
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video saved: {output_path}")
    return output_path

import requests
import os
from config import OUTPUT_DIR, CHARACTER_PROMPT

def generate_image(prompt, output_filename, width=1920, height=1080):
    print(f"🎨 Generating image: {output_filename} ({width}x{height})...")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width={width}&height={height}&nologo=true"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Image saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️ Image generation failed: {e}")
        # Create a solid black fallback image if AI fails
        from PIL import Image
        img = Image.new('RGB', (width, height), color='black')
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(output_path)
        return output_path

def create_visuals(topic, is_short=False):
    # 1. Set dimensions based on video type
    if is_short:
        width, height = 1080, 1920  # Vertical for Shorts
    else:
        width, height = 1920, 1080  # Horizontal for Long videos

    # 2. Generate the background
    bg_prompt = f"Cinematic, highly detailed, 2D vector art background for a YouTube video about {topic}. Clean, minimal, bright."
    bg_path = generate_image(bg_prompt, f"bg_{topic.replace(' ', '_')}.jpg", width=width, height=height)
    
    # 3. Generate the consistent main character (Magnus)
    char_path = generate_image(CHARACTER_PROMPT, "magnus_character.png", width=512, height=512)
    
    return bg_path, char_path

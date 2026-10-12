from PIL import Image, ImageDraw, ImageFont
import os
from config import OUTPUT_DIR

def create_thumbnail(topic, bg_path, char_path, output_filename):
    print(f"🖼️ Creating thumbnail for {topic}...")
    
    # Open base background
    base = Image.open(bg_path).resize((1280, 720)) # Standard YouTube thumbnail size
    
    # Paste the character in the bottom right
    char = Image.open(char_path).convert("RGBA")
    char = char.resize((400, 400))
    base.paste(char, (850, 300), char)
    
    # Add Text
    draw = ImageDraw.Draw(base)
    # Using a default bold font (you can upload a custom .ttf file later)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
    except:
        font = ImageFont.load_default()
    
    # Shorten text for thumbnail
    text = topic.upper()
    if len(text) > 30:
        text = text[:27] + "..."
        
    # Draw text with outline
    text_x = 50
    text_y = 50
    outline_color = "black"
    text_color = "white"
    
    # Draw outline
    for adj in range(-3, 4):
        for adj2 in range(-3, 4):
            draw.text((text_x+adj, text_y+adj2), text, font=font, fill=outline_color)
    # Draw main text
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    base.save(output_path)
    print(f"✅ Thumbnail saved: {output_path}")
    return output_path

import requests
import os
import random
import time
from config import OUTPUT_DIR, IMAGE_STYLE

# Rotating pool of finance / business / motivational visual templates
FINANCE_VISUALS = [
    "a lone businessman standing on a rooftop looking at a city skyline at dusk",
    "close-up of gold coins stacked on a wooden desk with warm lamp light",
    "a person walking up a long staircase toward a bright light",
    "an open leather wallet with dollar bills and a coffee cup",
    "a chessboard with a king piece standing under dramatic spotlight",
    "a man in a suit looking out a rainy window at night",
    "a young man sitting alone in a dark room reading a book by lamplight",
    "empty meeting room with chairs and a projector screen at dawn",
    "hands writing in a notebook next to a cup of coffee and a laptop",
    "an old clock on a wall with sunlight casting long shadows",
    "a mountain peak at sunrise with a single hiker silhouette",
    "a road stretching into the distance through a desert at sunset",
    "a wall covered in sticky notes and business plans",
    "a lighthouse standing against a stormy dark ocean",
    "a candle burning on a wooden table in a dark room",
    "money bills floating in the air in slow motion",
    "a glass jar full of coins on a kitchen table",
    "a family photo on a desk with a calculator and bills",
    "a gym at dawn with light coming through the windows",
    "a man in a hoodie staring at his reflection in a shop window",
    "an empty office at night with one desk lamp on",
    "a stack of books with the top one glowing softly",
    "a sunrise over a quiet suburban neighborhood",
    "a businessman shaking hands with a shadowy figure",
    "a young boy looking at a skyscraper from the street below",
    "an escalator going up in a modern glass building",
    "a plant growing out of dry cracked soil at sunrise",
    "a coin flipping in mid-air with motion blur",
    "a door slightly open with bright light pouring through the crack",
    "an old man's hands holding a worn-out wallet",
    "a car driving away on an empty highway at twilight",
    "a silhouette of a person standing on a cliff at sunset",
    "an hourglass with sand falling under warm golden light",
    "a hand reaching up toward the sky through bars of light",
    "a wooden boat on a calm sea at sunrise",
]


def generate_image(prompt, output_path, width, height, seed=None):
    """Generate a cinematic image via Pollinations.ai (free)."""
    full_prompt = f"{prompt}, {IMAGE_STYLE}"
    url = (
        f"https://image.pollinations.ai/prompt/"
        f"{requests.utils.quote(full_prompt)}"
        f"?width={width}&height={height}&nologo=true&model=flux"
    )
    if seed is not None:
        url += f"&seed={seed}"

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=180)
            response.raise_for_status()
            if len(response.content) < 5000:
                raise Exception("Image too small — likely failed")
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        except Exception as e:
            print(f"⚠️ Image attempt {attempt+1} failed: {e}")
            time.sleep(3)

    # Fallback: solid dark image
    from PIL import Image
    Image.new("RGB", (width, height), (20, 20, 30)).save(output_path)
    return output_path


def create_visuals(topic, num_images, is_short=False):
    """Generate N cinematic images for this video."""
    if is_short:
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    # Pick N unique visual templates
    pool = FINANCE_VISUALS.copy()
    random.shuffle(pool)
    selected = pool[:num_images]

    paths = []
    for i, visual in enumerate(selected):
        # Add topic flavor to the prompt
        prompt = f"{visual}, related to {topic}"
        path = os.path.join(OUTPUT_DIR, f"img_{i:03d}.jpg")
        print(f"🎨 [{i+1}/{num_images}] {visual[:60]}...")
        generate_image(prompt, path, width, height, seed=random.randint(1, 999999))
        paths.append(path)

    return paths

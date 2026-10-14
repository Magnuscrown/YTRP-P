import requests
import os
import random
import time
from config import OUTPUT_DIR, IMAGE_STYLE

CINEMATIC_MODIFIERS = [
    "dramatic golden hour lighting",
    "moody blue hour atmosphere",
    "soft morning light through a window",
    "warm lamp light in a dark room",
    "harsh noir shadows",
    "rainy night neon reflections",
    "dusty sunlight beams",
    "cool overcast daylight",
    "firelight glow",
    "candlelit warm interior",
    "sunset silhouette",
    "foggy dawn mist",
    "cinematic backlight with lens flare",
    "single spotlight on subject",
]

COMPOSITIONS = [
    "wide establishing shot",
    "medium shot",
    "close-up detail shot",
    "low angle heroic shot",
    "over-the-shoulder shot",
    "top-down flat lay",
    "silhouette against bright background",
    "isolated subject with negative space",
    "environmental portrait",
    "documentary style candid",
]

SETTINGS = [
    "a modern city skyline at dusk",
    "a quiet library with old books",
    "a minimalist home office with laptop",
    "a rainy window overlooking traffic",
    "an empty boardroom with leather chairs",
    "a garage workshop with tools",
    "a rooftop garden with potted plants",
    "a coffee shop with warm wood counters",
    "a dirt road through farmland at sunrise",
    "a glass skyscraper lobby",
    "a subway platform at night",
    "an old brick warehouse interior",
    "a mountain trail with morning mist",
    "a fishing boat on a calm sea",
    "a train station with a lone traveler",
    "a walk-up apartment stairwell",
    "an old man's cluttered desk",
    "a young person's empty bedroom",
    "a farm at golden hour",
    "a bookstore window display",
    "a mountain cabin with snow",
    "a pier at sunset",
    "a rooftop overlooking a bridge",
    "a university library staircase",
    "a fire escape at night",
    "a basketball court at sunset",
    "a boxing gym interior",
]


def build_prompt(topic, index):
    setting = random.choice(SETTINGS)
    lighting = random.choice(CINEMATIC_MODIFIERS)
    comp = random.choice(COMPOSITIONS)
    subject = f"symbolic visual about {topic}"
    return (
        f"{subject}, {setting}, {comp}, {lighting}, "
        f"no text, no watermark, no logo, no caption"
    )


def generate_image(prompt, output_path, width, height, seed=None):
    full_prompt = f"{prompt}, {IMAGE_STYLE}"

    # Pollinations free endpoint — no model parameter (flux costs money now)
    # Random subdomain helps distribute load and reduces rate limits
    subdomain = random.choice(["image", "image", "image", "image2", "image3"])
    url = (
        f"https://{subdomain}.pollinations.ai/prompt/"
        f"{requests.utils.quote(full_prompt)}"
        f"?width={width}&height={height}&nologo=true"
    )
    if seed is not None:
        url += f"&seed={seed}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, timeout=240)
            if r.status_code == 402:
                print(f"   ⚠️ 402 Payment Required — Pollinations might need a delay")
                time.sleep(10)
                continue
            r.raise_for_status()
            if len(r.content) < 5000:
                raise Exception("Image too small")
            with open(output_path, "wb") as f:
                f.write(r.content)
            return output_path
        except Exception as e:
            print(f"   ⚠️ attempt {attempt+1}/5 failed: {repr(e)[:120]}")
            time.sleep(8)

    # Fallback: dark gradient placeholder
    from PIL import Image
    print(f"   ⚠️ All attempts failed — using placeholder image")
    Image.new("RGB", (width, height), (20, 20, 30)).save(output_path)
    return output_path


def create_visuals(topic, num_images, is_short=False):
    if is_short:
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    paths = []
    for i in range(num_images):
        prompt = build_prompt(topic, i)
        path = os.path.join(OUTPUT_DIR, f"img_{i:03d}.jpg")
        print(f"🎨 [{i+1}/{num_images}] {prompt[:70]}...")
        generate_image(prompt, path, width, height, seed=random.randint(1, 999999))
        # Small delay between requests to avoid hammering their rate limit
        time.sleep(2)
        paths.append(path)

    return paths

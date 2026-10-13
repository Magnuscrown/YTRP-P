import os
from trend_researcher import research_topics
from script_writer import write_script
from voiceover import make_voice
from visuals import create_visuals
from render import render_video
from config import OUTPUT_DIR, IMAGES_LONG, IMAGES_SHORT


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("🚀 Magnus AI Machine — Cinematic Finance Edition")
    topics = research_topics()
    print(f"📌 Topics: {topics}")

    pipeline = [
        ("long_finance", "long", False, IMAGES_LONG),
        ("long_general", "long", False, IMAGES_LONG),
        ("short_finance", "short", True, IMAGES_SHORT),
        ("short_general", "short", True, IMAGES_SHORT),
        ("short_curious", "short", True, IMAGES_SHORT),
    ]

    for key, video_type, is_short, num_images in pipeline:
        topic = topics[key]
        print(f"\n━━━ 🎬 {key.upper()}: {topic} ━━━")

        # 1. Script
        script = write_script(topic, video_type)
        with open(f"{OUTPUT_DIR}/{key}.txt", "w") as f:
            f.write(script)

        # 2. Voice
        audio = f"{key}.mp3"
        make_voice(script, audio)

        # 3. Images
        images = create_visuals(topic, num_images, is_short)

        # 4. Render
        render_video(images, os.path.join(OUTPUT_DIR, audio), topic, is_short)

    print("\n✅ ALL DONE. Check output/ folder.")


if __name__ == "__main__":
    main()

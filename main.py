import os
from trend_researcher import research_topics
from script_writer import write_script
from voiceover import make_voice
from visuals import create_visuals
from thumbnail import create_thumbnail
from render import render_video
from config import OUTPUT_DIR

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("🚀 Starting Magnus YouTube AI Machine...")

    # Step 1: Find Topics
    topics = research_topics()
    print(f"📌 Topics Found: {topics}")

    # Define our video pipeline: (topic_key, video_type, is_short)
    pipeline = [
        ("long_finance", "long", False),
        ("long_general", "long", False),
        ("short_finance", "short", True),
        ("short_general", "short", True),
        ("short_curious", "short", True)
    ]

    for topic_key, video_type, is_short in pipeline:
        topic = topics[topic_key]
        print(f"\n--- 🎬 Processing: {topic} ---")

        # 1. Write Script
        script = write_script(topic, video_type)
        
        # Save script text
        with open(f"{OUTPUT_DIR}/{topic_key}.txt", "w") as f:
            f.write(script)

        # 2. Generate Voice
        audio_path = f"{topic_key}_voice.mp3"
        make_voice(script, audio_path)
        
        # 3. Generate Visuals (Background + Character) - NOW WITH ORIENTATION
        bg_path, char_path = create_visuals(topic, is_short)

        # 4. Create Thumbnail
        thumb_name = f"{topic_key}_thumbnail.jpg"
        create_thumbnail(topic, bg_path, char_path, thumb_name)

        # 5. Render Video
        render_video(bg_path, char_path, os.path.join(OUTPUT_DIR, audio_path), topic, is_short)

    print("\n✅ Machine run complete! Check the output folder.")

if __name__ == "__main__":
    main()

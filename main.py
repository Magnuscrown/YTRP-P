import os
from trend_researcher import research_topics
from script_writer import write_script
from voiceover import make_voice
from config import OUTPUT_DIR

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("🚀 Starting Magnus AI Machine (Script + Voice Only)...")
    topics = research_topics()
    print(f"📌 Topics: {topics}")

    pipeline = [
        ("long_finance", "long"),
        ("long_general", "long"),
        ("short_finance", "short"),
        ("short_general", "short"),
        ("short_curious", "short")
    ]

    for topic_key, video_type in pipeline:
        topic = topics[topic_key]
        print(f"\n--- 🎬 Processing: {topic} ---")

        # 1. Write script
        script = write_script(topic, video_type)
        script_path = f"{OUTPUT_DIR}/{topic_key}.txt"
        with open(script_path, "w") as f:
            f.write(script)
        print(f"📄 Script saved: {script_path}")

        # 2. Generate voice
        audio_filename = f"{topic_key}.mp3"
        make_voice(script, audio_filename)

    print("\n✅ DONE. Download the artifact to hear your voices.")

if __name__ == "__main__":
    main()

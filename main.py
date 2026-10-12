import os
from trend_researcher import research_topics
from script_writer import write_script
from config import OUTPUT_DIR

def main():
    # Create output folder
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("🚀 Starting Magnus YouTube AI Machine...")

    # Step 1: Find Topics
    topics = research_topics()
    print(f"📌 Topics Found: {topics}")

    # Step 2: Write Scripts (2 Long, 3 Short)
    print("📝 Writing Long Scripts...")
    long_finance_script = write_script(topics['long_finance'], "long")
    long_general_script = write_script(topics['long_general'], "long")

    print("📝 Writing Short Scripts...")
    short_finance_script = write_script(topics['short_finance'], "short")
    short_general_script = write_script(topics['short_general'], "short")
    short_curious_script = write_script(topics['short_curious'], "short")

    # Save scripts to output folder
    with open(f"{OUTPUT_DIR}/1_long_finance.txt", "w") as f:
        f.write(long_finance_script)
    with open(f"{OUTPUT_DIR}/2_long_general.txt", "w") as f:
        f.write(long_general_script)
    with open(f"{OUTPUT_DIR}/3_short_finance.txt", "w") as f:
        f.write(short_finance_script)
    with open(f"{OUTPUT_DIR}/4_short_general.txt", "w") as f:
        f.write(short_general_script)
    with open(f"{OUTPUT_DIR}/5_short_curious.txt", "w") as f:
        f.write(short_curious_script)

    print("✅ Scripts generated and saved to output folder!")

if __name__ == "__main__":
    main()

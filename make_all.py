"""
STEP 3: make every part of out/series.json, then join them into one long video.
Run:  python make_all.py        (TEST_MODE=1 for a fake-image test)
Output: out/part_01.mp4 ... out/part_10.mp4  and  out/long.mp4
"""
import json, os, subprocess
import make_video


def main():
    series = json.load(open("out/series.json"))
    nums = [p["part"] for p in series["parts"]]
    for n in nums:
        print(f"--- making part {n}/{len(nums)} ---")
        make_video.build(n)

    with open("out/long_list.txt", "w") as f:
        for n in nums:
            f.write(f"file '{os.path.abspath(f'out/part_{n:02d}.mp4')}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "out/long_list.txt",
                    "-c", "copy", "out/long.mp4"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("Saved out/long.mp4")


if __name__ == "__main__":
    main()

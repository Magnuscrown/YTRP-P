"""
STEP 3: make every part of out/series.json, then join them into one long video.
Run:  python make_all.py        (TEST_MODE=1 for a fake-image test)
Output: out/part_01.mp4 ... out/part_10.mp4  and  out/long.mp4
"""
import argparse, json, os, subprocess
import make_video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="", help="e.g. 1 or 2,3,4 (default: all)")
    ap.add_argument("--concat", default="yes", help="join the parts into out/long.mp4 (yes/no)")
    args = ap.parse_args()
    series = json.load(open("out/series.json"))
    if args.parts:
        wanted = {int(x) for x in args.parts.split(",")}
        series["parts"] = [p for p in series["parts"] if p["part"] in wanted]
    budget = int(os.getenv("IMAGE_BUDGET") or 150)   # free Cloudflare allowance is roughly 170-230 images a day
    used, made = 0, []
    for p in series["parts"]:
        need = make_video.images_needed(p)
        if used + need > budget:
            print(f"[stop] part {p['part']} needs {need} images, only {budget - used} left in today's budget "
                  f"({budget}). Stopping here; parts {p['part']}+ can be made tomorrow.")
            break
        print(f"--- making part {p['part']} ({need} images, {used}/{budget} used so far) ---")
        make_video.build(p["part"])
        used += need
        made.append(p["part"])
    if not made:
        raise SystemExit("Nothing was made: budget too small for even one part.")

    if args.concat.lower() == "no":
        print(f"Made parts {made} ({used} images)")
        return
    with open("out/long_list.txt", "w") as f:
        for n in made:
            f.write(f"file '{os.path.abspath(f'out/part_{n:02d}.mp4')}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "out/long_list.txt",
                    "-c", "copy", "out/long.mp4"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print(f"Saved out/long.mp4 (parts {made[0]}-{made[-1]}, {used} images used)")


if __name__ == "__main__":
    main()

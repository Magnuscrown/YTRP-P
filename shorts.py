"""
SHORTS MAKER: turns out/recap.mp4 (horizontal) into vertical 9:16 Shorts, "Part 1/N", "Part 2/N" ...
  python shorts.py                      (about 2.5 min per part, never over 2:55 including the end card)
  python shorts.py --seconds 120        (shorter parts)    --title "Full video title"
Each part: blurred background + the film centred, big captions, "PART x/N" label.
The LAST part ends with a 4-second card: "Watch the full video on my channel" + the long video's title.
Reads: out/recap.mp4, out/timeline.json (made by recap.py).   Writes: out/shorts/part_01.mp4 ...
"""
import os, re, json, argparse, subprocess, textwrap

OUT = "out"
MAX_LEN = 170          # Shorts can be up to 3 minutes; keep room for the end card
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
END_CARD = 4


def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def group(timeline, target):
    """Group whole narration sections into parts, so a sentence is never cut in half."""
    parts, cur = [], []
    for s in timeline:
        if cur and s["t1"] - cur[0]["t0"] > MAX_LEN:
            parts.append(cur)
            cur = []
        cur.append(s)
        if cur[-1]["t1"] - cur[0]["t0"] >= target:
            parts.append(cur)
            cur = []
    if cur:
        if parts and cur[-1]["t1"] - cur[0]["t0"] < target * 0.4 \
                and parts[-1][-1]["t1"] - parts[-1][0]["t0"] + cur[-1]["t1"] - cur[0]["t0"] <= MAX_LEN:
            parts[-1] += cur
        else:
            parts.append(cur)
    return parts


def ts(x):
    h, m, s = int(x // 3600), int(x % 3600 // 60), x % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def write_srt(part, path, words_per_line=5):
    t0 = part[0]["t0"]
    lines, n = [], 1
    for s in part:
        words = s["narration"].split()
        chunks = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)] or [[]]
        dur = s["t1"] - s["t0"]
        cur = s["t0"] - t0
        for c in chunks:
            d = dur * len(c) / max(1, len(words))
            lines.append(f"{n}\n{ts(cur)} --> {ts(cur + d)}\n{' '.join(c)}\n")
            cur += d
            n += 1
    open(path, "w").write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=150)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    timeline = json.load(open(f"{OUT}/timeline.json"))
    title = a.title
    if not title and os.path.exists(f"{OUT}/titles.txt"):
        title = open(f"{OUT}/titles.txt").read().split("\n")[0]
    if not title and os.path.exists(f"{OUT}/source.json"):
        title = json.load(open(f"{OUT}/source.json")).get("title", "")
    parts = group(timeline, a.seconds)
    os.makedirs(f"{OUT}/shorts", exist_ok=True)

    for n, part in enumerate(parts, 1):
        last = n == len(parts)
        start, dur = part[0]["t0"], part[-1]["t1"] - part[0]["t0"]
        srt = f"{OUT}/shorts/p{n:02d}.srt"
        write_srt(part, srt)
        label = f"{OUT}/shorts/label{n:02d}.txt"
        open(label, "w").write(f"PART {n}/{len(parts)}")
        vf = ("[0:v]split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:6[bg];"
              "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v0];")
        chain = "[v0]"
        if last:
            vf += f"{chain}tpad=stop_mode=clone:stop_duration={END_CARD}[v1];"
            chain = "[v1]"
        vf += (f"{chain}subtitles=filename='{srt}':force_style='FontName=DejaVu Sans,FontSize=11,Bold=1,"
               f"Alignment=2,MarginV=55,Outline=3,Shadow=0'[v2];"
               f"[v2]drawtext=fontfile={FONT}:textfile={label}:fontsize=72:fontcolor=white:borderw=5:"
               f"bordercolor=black:x=(w-text_w)/2:y=170")
        if last:
            card = f"{OUT}/shorts/card.txt"
            wrapped = "\n".join(textwrap.wrap(title, 24)) if title else ""
            open(card, "w").write("Want the full story?\nWatch the FULL video\non my channel:\n\n" + wrapped)
            vf += (f"[v3];[v3]drawtext=fontfile={FONT}:textfile={card}:fontsize=64:fontcolor=white:"
                   f"box=1:boxcolor=black@0.7:boxborderw=40:line_spacing=14:x=(w-text_w)/2:y=(h-text_h)/2:"
                   f"enable='gte(t,{dur:.2f})'")
        out = f"{OUT}/shorts/part_{n:02d}.mp4"
        cmd = ["ffmpeg", "-y", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", f"{OUT}/recap.mp4",
               "-filter_complex", vf]
        if last:
            cmd += ["-af", f"apad=pad_dur={END_CARD}", "-t", f"{dur + END_CARD:.2f}"]
        cmd += ["-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
        sh(cmd)
        print(f"[ok] {out} ({dur + (END_CARD if last else 0):.0f}s)")
    print(f"Made {len(parts)} Shorts in {OUT}/shorts/")


if __name__ == "__main__":
    main()

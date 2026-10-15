"""Magnus AI (Finance Edition): 1 long + 3 shorts per run."""
import shutil
import sys
import traceback

import config as C
import trend_researcher
import script_writer
import voiceover
import scene_planner
import visuals
import render

ALLOWED = {"long_finance.mp4", "long_finance.txt"} | {f"short_finance_{i}.{e}" for i in (1, 2, 3) for e in ("mp4", "txt")}


def _distance(total, lo, hi):
    return 0 if lo <= total <= hi else (lo - total if total < lo else total - hi)


def make_video(kind, topic, name):
    spec = C.SPECS[kind]
    work = C.WORK_DIR / name
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    print(f"\n=== {name}: {topic} ===")
    try:
        best = None
        lo, hi = spec["min_sec"], spec["max_sec"]
        for attempt in range(spec["script_attempts"]):
            script = script_writer.write(kind, topic)
            audio, sents, durs = voiceover.synthesize(script, work, tag=f"voice{attempt}")
            total = sum(durs)
            dist = _distance(total, lo, hi)
            if best is None or dist < best[0]:
                best = (dist, script, audio, sents, durs)
            if dist == 0:
                break
            print(f"[length] {total:.0f}s is outside {lo}-{hi}s, retrying")
        _, script, audio, sents, durs = best

        scenes = scene_planner.build_scenes(sents, durs)
        vis = scene_planner.plan_visuals(scenes, topic, spec["max_images"])
        key_paths = visuals.generate(vis, work)
        visuals.resolve_paths(scenes, key_paths)

        out_mp4 = C.OUTPUT_DIR / f"{name}.mp4"
        dur = render.render_video(scenes, audio, spec["size"], out_mp4)
        (C.OUTPUT_DIR / f"{name}.txt").write_text(f"TOPIC: {topic}\n\n{script}\n", encoding="utf-8")
        if dur < (spec.get("hard_min_sec") or spec["min_sec"] - 5):
            print(f"[WARN] {name} is only {dur:.0f}s, under the minimum")
        print(f"[done] {name}: {dur / 60:.1f} min")
        trend_researcher.mark_used(topic)
        return True
    except Exception:
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    C.OUTPUT_DIR.mkdir(exist_ok=True)
    C.WORK_DIR.mkdir(exist_ok=True)
    for k in ("OPENROUTER_API_KEY", "CF_ACCOUNT_ID", "CF_API_TOKEN"):
        if not getattr(C, k):
            print(f"[WARN] {k} is not set")
    long_topics, short_topics, spares = trend_researcher.pick_topics(1, 3)
    jobs = [("long", long_topics[0], "long_finance")]
    jobs += [("short", t, f"short_finance_{i}") for i, t in enumerate(short_topics, 1)]
    results, failed = [], []
    for kind, topic, name in jobs:
        ok, tries = False, [topic]
        while tries and not ok:
            t = tries.pop(0)
            ok = make_video(kind, t, name) or make_video(kind, t, name)   # 2 tries per topic
            if not ok and spares:
                tries.append(spares.pop(0))                               # then a fresh topic
                print(f"[retry] {name} failed twice, trying a new topic")
            if not ok and len(tries) == 0:
                break
        results.append(ok)
        if not ok:
            failed.append(name)
    shutil.rmtree(C.WORK_DIR, ignore_errors=True)
    for f in C.OUTPUT_DIR.iterdir():            # keep ONLY final videos + scripts
        if f.name not in ALLOWED:
            f.unlink() if f.is_file() else shutil.rmtree(f, ignore_errors=True)
    print(f"\nFinished: {sum(results)}/{len(results)} videos")
    if failed:
        print("FAILED VIDEOS: " + ", ".join(failed) + "  (scroll up for the error of each one)")
    sys.exit(0 if any(results) else 1)


if __name__ == "__main__":
    main()

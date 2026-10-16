"""Magnus Stickman Rich vs Poor Psychology: 1 long + 3 shorts per run."""
import shutil, sys, traceback
import config as C
import topic_generator, script_writer, voiceover, scene_timing, scene_planner, render

ALLOWED = {"long_lists.mp4", "long_lists.txt"} | {f"short_lists_{i}.{e}" for i in (1, 2, 3) for e in ("mp4", "txt")}

def _distance(total, lo, hi):
    return 0 if lo <= total <= hi else (lo - total if total < lo else total - hi)

def make_video(job, name):
    spec = C.SPECS[job["kind"]]
    work = C.WORK_DIR / name
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    print(f"\n=== {name}: {job['title']} ===")
    try:
        outline = script_writer.get_outline(job)
        best, lo, hi = None, spec["min_sec"], spec["max_sec"]
        for attempt in range(spec["script_attempts"]):
            script = script_writer.write(job, outline=outline)
            audio, sents, durs = voiceover.synthesize(script, work, tag=f"voice{attempt}")
            total = sum(durs); dist = _distance(total, lo, hi)
            if best is None or dist < best[0]: best = (dist, script, audio, sents, durs)
            if dist == 0: break
            print(f"[length] {total:.0f}s is outside {lo}-{hi}s, retrying")
        _, script, audio, sents, durs = best
        scenes = scene_timing.build_scenes(sents, durs)
        scene_planner.plan_scenes(scenes, job["title"])
        out_mp4 = C.OUTPUT_DIR / f"{name}.mp4"
        dur = render.render_video(scenes, audio, spec["size"], out_mp4)
        (C.OUTPUT_DIR / f"{name}.txt").write_text(f"TITLE: {job['title']}\n\n{script}\n", encoding="utf-8")
        if dur < (spec.get("hard_min_sec") or spec["min_sec"] - 5):
            print(f"[WARN] {name} is only {dur:.0f}s, under the minimum")
        print(f"[done] {name}: {dur / 60:.1f} min")
        topic_generator.mark_used(job["title"]); return True
    except Exception:
        traceback.print_exc(); return False
    finally:
        shutil.rmtree(work, ignore_errors=True)

def main():
    C.OUTPUT_DIR.mkdir(exist_ok=True); C.WORK_DIR.mkdir(exist_ok=True)
    if not C.OPENROUTER_API_KEY: print("[WARN] OPENROUTER_API_KEY is not set")
    jobs = topic_generator.pick_jobs()
    names = ["long_lists", "short_lists_1", "short_lists_2", "short_lists_3"]
    results, failed = [], []
    for job, name in zip(jobs, names):
        ok = make_video(job, name) or make_video(job, name)
        if not ok:
            try:
                alt = topic_generator.new_job(job["kind"])
                print(f"[retry] {name} failed twice, trying a new title")
                ok = make_video(alt, name)
            except Exception: traceback.print_exc()
        results.append(ok)
        if not ok: failed.append(name)
    shutil.rmtree(C.WORK_DIR, ignore_errors=True)
    for f in C.OUTPUT_DIR.iterdir():
        if f.name not in ALLOWED:
            f.unlink() if f.is_file() else shutil.rmtree(f, ignore_errors=True)
    print(f"\nFinished: {sum(results)}/{len(results)} videos")
    if failed: print("FAILED VIDEOS: " + ", ".join(failed) + "  (scroll up for the error of each one)")
    sys.exit(0 if any(results) else 1)

if __name__ == "__main__":
    main()

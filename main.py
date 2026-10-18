"""Magnus Stickman Rich vs Poor Psychology: 1 long + 3 shorts per run, each with a different angle, hook and ending, plus a thumbnail."""
import shutil, sys, traceback
import config as C
import topic_generator, script_writer, voiceover, scene_timing, scene_planner, render
import thumbnail

NAMES = ["long_lists", "short_lists_1", "short_lists_2", "short_lists_3"]
ALLOWED = ({f"{n}.{e}" for n in NAMES for e in ("mp4", "txt")}
           | {f"{n}_thumb.jpg" for n in NAMES})

def _distance(total, lo, hi):
    return 0 if lo <= total <= hi else (lo - total if total < lo else total - hi)

def make_video(job, name):
    spec = C.SPECS[job["kind"]]
    work = C.WORK_DIR / name
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    print(f"\n=== {name} [{job.get('fmt')}/{job.get('hook_style')}/{job.get('ending')}]: {job['title']} ===")
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
        scene_planner.plan_scenes(scenes, job["title"], job.get("fmt"))
        out_mp4 = C.OUTPUT_DIR / f"{name}.mp4"
        dur = render.render_video(scenes, audio, spec["size"], out_mp4)
        thumb_text = ""
        try:
            thumb_text = thumbnail.make_thumbnail(job, C.OUTPUT_DIR / f"{name}_thumb.jpg", script=script)
        except Exception:
            print(f"[WARN] thumbnail failed for {name}"); traceback.print_exc()
        (C.OUTPUT_DIR / f"{name}.txt").write_text(
            f"TITLE: {job['title']}\nANGLE: {job.get('fmt')} | HOOK: {job.get('hook_style')} | ENDING: {job.get('ending')}\nTHUMBNAIL TEXT: {thumb_text}\n\n{script}\n", encoding="utf-8")
        if dur < (spec.get("hard_min_sec") or spec["min_sec"] - 5):
            print(f"[WARN] {name} is only {dur:.0f}s, under the minimum")
        print(f"[done] {name}: {dur / 60:.1f} min")
        topic_generator.mark_used(job["title"], job.get("fmt"), job.get("hook_style"), job.get("ending"), job.get("tpl", "")[7:] if job.get("tpl", "").startswith("search:") else None); return True
    except Exception:
        traceback.print_exc(); return False
    finally:
        shutil.rmtree(work, ignore_errors=True)

def main():
    C.OUTPUT_DIR.mkdir(exist_ok=True); C.WORK_DIR.mkdir(exist_ok=True)
    if not C.OPENROUTER_API_KEY: print("[WARN] OPENROUTER_API_KEY is not set")
    jobs = topic_generator.pick_jobs()
    pairs = list(zip(jobs, NAMES))
    # shorts first (fast, guaranteed 3 videos), the long video last
    pairs.sort(key=lambda p: p[0]["kind"] == "long")
    results, failed = [], []
    for job, name in pairs:
        ok = make_video(job, name) or make_video(job, name)
        if not ok:
            for _ in range(2):
                try:
                    alt = topic_generator.new_job(job["kind"], fmt=job.get("fmt"), hook_style=job.get("hook_style"), ending=job.get("ending"))
                    print(f"[retry] {name} failed twice, trying a new title")
                    ok = make_video(alt, name)
                    if ok: break
                except Exception:
                    traceback.print_exc()
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

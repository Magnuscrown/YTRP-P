"""
LEVEL 2 TEST: does your Gemini key let us make small ACTION pictures (blink, raised hand) from a normal picture?
  python test_edit.py "cartoon man at a kitchen table counting coins" "eyes closed in a blink"
Writes out/test_original.png and out/test_edited.png. Open both: same character, only a tiny change = it works.
"""
import os, sys, shutil
os.makedirs("out", exist_ok=True)
import make_video as mv

prompt = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "clean 3D cartoon young man at a kitchen table counting coins, bright colours"
edit = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else "eyes closed in a blink"
mv.make_image(prompt + ", no text, no watermark", "out/test_original.png", 0)
print("[ok] original picture made")
res = mv.make_edit("out/test_original.png", edit)
if res:
    shutil.copy(res, "out/test_edited.png")
    print("[ok] ACTION PICTURE WORKS: compare out/test_original.png and out/test_edited.png")
else:
    print("[no] the action picture did not work with your key right now (see [edit] lines above). "
          "The video still works: those beats just use the normal picture.")

"""Build the Kaggle upload bundles into outputs/kaggle_upload/.

video_bundle.zip    — manifest_shots.json + every keyframe the manifest lists
manifest_music.json — copied as a plain file (single upload)

Paths come straight from the manifest's "image" fields (Kaggle layout:
"keyframes/<name>" relative to /kaggle/working), mapped back to
outputs/keyframes/<name> here. Naming-agnostic: whatever the keyframes
stage writes and shots.py references is what gets bundled. Idempotent.
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYFRAMES = ROOT / "outputs" / "keyframes"
OUT = ROOT / "outputs" / "kaggle_upload"


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    shots_manifest = ROOT / "kaggle" / "manifest_shots.json"
    if not shots_manifest.exists():
        sys.exit("no kaggle/manifest_shots.json — run: make shots")
    shots = json.loads(shots_manifest.read_text())

    zpath = OUT / "video_bundle.zip"
    missing = []
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(shots_manifest, "manifest_shots.json")
        for s in shots["shots"]:
            rel = s["image"]                      # e.g. keyframes/s1_das.png
            local = KEYFRAMES / Path(rel).name    # outputs/keyframes/s1_das.png
            if local.exists():
                z.write(local, rel)
            else:
                missing.append(rel)
    if missing:
        sys.exit("video bundle incomplete — keyframes referenced by the manifest "
                 "but missing on disk: %s\nrun: make keyframes"
                 % ", ".join(missing))
    print("video bundle ready -> %s (%d KB, %d keyframes)"
          % (zpath, zpath.stat().st_size // 1024, len(shots["shots"])))

    music_manifest = ROOT / "kaggle" / "manifest_music.json"
    if music_manifest.exists():
        dst = OUT / "manifest_music.json"
        shutil.copy(music_manifest, dst)
        mf = json.loads(music_manifest.read_text())
        print("music manifest ready -> %s (%.0fs, seeds %s)"
              % (dst, mf["seconds"], mf["seeds"]))
    else:
        print("music manifest NOT ready — run: make music")


if __name__ == "__main__":
    main()

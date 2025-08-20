import json, shutil, pathlib, time, sys

PLAN = pathlib.Path("code_garden/plan.json")
ROOT = pathlib.Path(".")
ARCH = pathlib.Path("archive") / time.strftime("cg_%Y%m%d_%H%M%S")
ARCH.mkdir(parents=True, exist_ok=True)

if not PLAN.exists():
    print("No plan.json; run parse_reports.py first"); sys.exit(1)

plan = json.loads(PLAN.read_text())
moved = []
for item in plan["actions"]:
    f, action = item["file"], item["action"]
    p = ROOT / f
    if not p.exists(): continue
    if action == "quarantine":
        dest = ARCH / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dest)); moved.append((f, str(dest)))

print(f"Quarantined {len(moved)} files to {ARCH}")
(ARCH / "_moved.json").write_text(json.dumps(moved, indent=2))

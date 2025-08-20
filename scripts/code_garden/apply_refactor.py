import json, pathlib, sys, shutil

MAN = pathlib.Path("code_garden/refactor_preview/_manifest.json")
if not MAN.exists():
    print("No refactor preview manifest found; run split_large_modules.py"); sys.exit(1)

manifest = json.loads(MAN.read_text())

print("Select an index (0..n-1) to apply split for a module:")
for i, item in enumerate(manifest):
    print(i, "->", item["file"])

sel = input("Index to apply: ").strip()
if not sel.isdigit(): sys.exit(1)
i = int(sel)
item = manifest[i]
orig = pathlib.Path(item["file"])
preview_index = pathlib.Path(item["index"])
preview_dir = preview_index.parent

# Move preview parts into the original folder as a package subdir
pkg_dir = orig.parent / (orig.stem + "_pkg")
pkg_dir.mkdir(exist_ok=True)

for part in item["parts"] + [item["index"]]:
    src = pathlib.Path(part)
    dst = pkg_dir / src.name
    shutil.copy2(src, dst)

# Replace original file to import from the new package
orig.write_text(f"# Auto-split applied\nfrom .{pkg_dir.name}.{preview_index.stem} import *\n")

print(f"Applied split for {orig}")

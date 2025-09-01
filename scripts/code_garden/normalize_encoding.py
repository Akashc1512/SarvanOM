import pathlib, sys, tokenize, io

SKIP = ("venv",".venv","node_modules",".next","archive")
converted = []
for p in pathlib.Path(".").rglob("*.py"):
    sp = str(p)
    if any(seg in sp for seg in SKIP): 
        continue
    try:
        # detect declared encoding per PEP 263
        with tokenize.open(sp) as f:
            content = f.read()
        # re-write as utf-8 without BOM
        p.write_text(content, encoding="utf-8", errors="strict")
    except Exception as e:
        # last resort: decode as latin-1 and re-encode utf-8
        try:
            raw = p.read_bytes()
            p.write_text(raw.decode("latin-1"), encoding="utf-8", errors="ignore")
        except Exception:
            print(f"SKIP (encoding): {sp}", file=sys.stderr)
            continue
    converted.append(sp)
print(f"UTF-8 normalized: {len(converted)} files")

import pathlib, sys, py_compile

SKIP = ("venv", ".venv", "node_modules", ".next", "archive")
errors = []
for p in pathlib.Path(".").rglob("*.py"):
    sp = str(p)
    if any(seg in sp for seg in SKIP): 
        continue
    try:
        py_compile.compile(sp, doraise=True)
    except Exception as e:
        errors.append((sp, str(e)))

if errors:
    print("SYNTAX ERRORS:")
    for f, err in errors:
        print(f"- {f}: {err}")
    sys.exit(1)
print("Syntax OK")

import ast, pathlib, json, os

THRESHOLD = int(os.getenv("CG_SPLIT_LINES", "500"))
ROOT = pathlib.Path(".")
PREVIEW = pathlib.Path("code_garden/refactor_preview")
PREVIEW.mkdir(parents=True, exist_ok=True)

def split_file(path: pathlib.Path):
    text = path.read_text("utf-8", errors="ignore")
    if text.count("\n") < THRESHOLD: return None
    mod = ast.parse(text)
    classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
    funcs = [n for n in mod.body if isinstance(n, ast.FunctionDef)]
    if not classes and not funcs: return None

    base = PREVIEW / path.parent
    (base).mkdir(parents=True, exist_ok=True)
    parts = []

    for c in classes:
        out = base / f"{path.stem}_{c.name}.py"
        out.write_text(ast.get_source_segment(text, c) + "\n", encoding="utf-8")
        parts.append(str(out))

    helper = base / f"{path.stem}_helpers.py"
    if funcs:
        helper.write_text("\n\n".join(ast.get_source_segment(text, f) for f in funcs) + "\n", encoding="utf-8")
        parts.append(str(helper))

    index = base / f"{path.stem}__index.py"
    exports = [f"from .{path.stem}_{c.name} import {c.name}" for c in classes]
    if funcs: exports.append(f"from .{path.stem}_helpers import " + ", ".join(f.name for f in funcs))
    index.write_text("\n".join(exports) + "\n", encoding="utf-8")
    return {"file": str(path), "parts": parts, "index": str(index)}

def main():
    big = []
    for p in ROOT.rglob("*.py"):
        sp = str(p)
        if any(x in sp for x in ("/venv/","/archive/","/node_modules/","/.next/","/tests/")): continue
        res = split_file(p)
        if res: big.append(res)
    (PREVIEW / "_manifest.json").write_text(json.dumps(big, indent=2))
    print(f"Preview generated for {len(big)} file(s). See {PREVIEW}/_manifest.json")

if __name__ == "__main__":
    main()

import re, json, pathlib, fnmatch, sys, hashlib, time, yaml

ROOT = pathlib.Path(".").resolve()
REPORTS = ROOT / "reports"
RULES = ROOT / "code_garden" / "keep_rules.yml"
PLAN = ROOT / "code_garden" / "plan.json"

def read(path): return path.read_text(encoding="utf-8") if path.exists() else ""

def load_rules():
    if RULES.exists():
        return yaml.safe_load(RULES.read_text())
    return {"keep":[], "adopt":[], "quarantine":[]}

def match_any(path, patterns):
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)

def list_py_files():
    files = []
    for p in ROOT.rglob("*.py"):
        sp = str(p).replace("\\", "/")
        if any(seg.startswith(".") for seg in p.parts): continue
        if "/archive/" in sp or "/venv/" in sp or "/node_modules/" in sp or "/.next/" in sp or "/tests/" in sp:
            continue
        files.append(sp)
    return files

def parse_vulture():
    txt = read(REPORTS / "vulture.txt")
    suspects = set()
    for line in txt.splitlines():
        # format: path:line: score unused ...
        if ":" in line and ("unused" in line or "unreachable" in line):
            suspects.add(line.split(":")[0])
    return suspects

def parse_grimp_modules():
    d = json.loads(read(REPORTS / "import_graph.json") or "{}")
    return set(d.get("modules", [])), d.get("cycles", [])

def main():
    rules = load_rules()
    pyfiles = set(list_py_files())
    vulture_files = parse_vulture()
    modules, cycles = parse_grimp_modules()

    plan = {"generated_at": time.time(), "cycles": cycles, "actions": []}

    for f in sorted(pyfiles):
        action = "keep"
        if match_any(f, rules["quarantine"]): action = "quarantine"
        elif match_any(f, rules["adopt"]): action = "adopt"
        elif f in vulture_files: action = "quarantine"
        elif not any(f.startswith(prefix) for prefix in rules["keep"]): action = "adopt"
        plan["actions"].append({"file": f, "action": action})
    PLAN.write_text(json.dumps(plan, indent=2))
    print(f"Wrote plan to {PLAN}")

if __name__ == "__main__":
    main()

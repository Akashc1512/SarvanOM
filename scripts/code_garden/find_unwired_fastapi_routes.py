import ast, pathlib, json

ROOT = pathlib.Path(".")
routers = []      # modules defining APIRouter
includes = set()  # included router module names or variables

def module_name(p): return ".".join(p.with_suffix("").parts)

for p in ROOT.rglob("*.py"):
    sp = str(p).replace("\\", "/")
    if any(seg in sp for seg in ("/venv/","/archive/","/.next/","/node_modules/")): continue
    src = p.read_text("utf-8", errors="ignore")
    try: tree = ast.parse(src)
    except SyntaxError: continue

    # find APIRouter defs
    defined_router = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(getattr(node.func, "attr", None), "lower", lambda: "" )() == "apirouter":
            defined_router = True
            break
        if isinstance(node, ast.Call) and getattr(getattr(node.func, "id", None), "lower", lambda: "" )() == "apirouter":
            defined_router = True
            break
    if defined_router:
        routers.append({"module": module_name(p), "path": sp})

    # find include_router usage
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "include_router":
            includes.add(module_name(p))

print(json.dumps({"routers": routers, "includes": list(includes)}, indent=2))

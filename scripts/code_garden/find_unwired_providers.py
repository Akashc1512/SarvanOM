import ast, pathlib, json, re

ROOT = pathlib.Path(".")
providers = []  # classes that look like LLM providers
registry = set()

for p in ROOT.rglob("*.py"):
    sp = str(p).replace("\\", "/")
    if "/archive/" in sp or "/venv/" in sp or "/node_modules/" in sp: continue
    try: tree = ast.parse(p.read_text("utf-8", errors="ignore"))
    except SyntaxError: continue

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name.lower()
            if any(k in name for k in ("openai","anthropic","ollama","huggingface","llmclient","provider")):
                providers.append({"class": node.name, "module": ".".join(p.with_suffix("").parts), "path": sp})

        if isinstance(node, ast.Assign):
            # crude registry detection: PROVIDERS = {... 'openai': OpenAIClient, ...}
            if any(getattr(t, "id", "") == "PROVIDERS" for t in getattr(node.targets, "elts", [])) or \
               any(getattr(t, "id", "") == "PROVIDERS" for t in getattr(node.targets, "elts", [])):
                registry.add(".".join(p.with_suffix("").parts))

print(json.dumps({"providers": providers, "registries": list(registry)}, indent=2))

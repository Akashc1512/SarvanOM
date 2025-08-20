#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports

python -m pip install -U pip
pip install -r scripts/code_garden/requirements.txt

# 1) Dead/unused
vulture . \
  --min-confidence 70 \
  --exclude 'venv,**/archive/**,**/node_modules/**,**/build/**,**/.next/**,**/tests/**' \
  --sort-by-size > reports/vulture.txt || true

# 2) Complexity & Maintainability
radon cc -s -a -n B . > reports/radon_cc.txt || true
radon mi -s . > reports/radon_mi.txt || true

# 3) Imports graph (cycles, unused modules by import reachability)
python - <<'PY'
import json, sys
from grimp import build_graph
g = build_graph(sys.argv[1:])
scc = g.find_cycles()
print(json.dumps({"modules": list(g.modules), "cycles": [list(c) for c in scc]}, indent=2))
PY $(git ls-files '*.py') > reports/import_graph.json

# 4) Ruff diagnostics (style/smells), no fail
ruff check --exit-zero --output-format=github . > reports/ruff.txt || true

echo "Audit reports in ./reports"

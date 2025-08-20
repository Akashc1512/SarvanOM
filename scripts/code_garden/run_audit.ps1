#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path "reports" | Out-Null

python -m pip install -U pip
pip install -r scripts/code_garden/requirements.txt

# 1) Dead/unused
vulture . `
  --min-confidence 70 `
  --exclude 'venv,**/archive/**,**/node_modules/**,**/build/**,**/.next/**,**/tests/**' `
  --sort-by-size > reports/vulture.txt 2>$null

# 2) Complexity & Maintainability
radon cc -s -a -n B . > reports/radon_cc.txt 2>$null
radon mi -s . > reports/radon_mi.txt 2>$null

# 3) Imports graph (cycles, unused modules by import reachability)
$pythonCode = @"
import json, sys
from grimp import build_graph
g = build_graph(sys.argv[1:])
scc = g.find_cycles()
print(json.dumps({"modules": list(g.modules), "cycles": [list(c) for c in scc]}, indent=2))
"@

$pythonCode | python - (git ls-files '*.py') > reports/import_graph.json

# 4) Ruff diagnostics (style/smells), no fail
ruff check --exit-zero --output-format=github . > reports/ruff.txt 2>$null

Write-Host "Audit reports in ./reports"

param([int]$Threshold=500)
python -m pip install -U pip
python - <<'PY'
import sys, subprocess
subprocess.run([sys.executable,"scripts/code_garden/check_syntax.py"], check=True)
PY
set CG_SPLIT_LINES=$Threshold
python scripts/code_garden/split_large_modules.py

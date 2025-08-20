# Code Garden

1) `make cg-audit` → runs vulture/radon/ruff/grimp and writes reports/
2) `make cg-plan` → builds code_garden/plan.json from reports + keep_rules.yml
3) `make cg-apply` → quarantines unused/legacy files into archive/cg_*
4) `make cg-preview` → generates non-destructive refactor previews for large files (>500 lines)
5) `make cg-split` → interactively applies a selected split (safe import rewire)
6) `make cg-restore` → restores last archive (manual copy back)

Check plan.json before applying. All actions are reversible.

# Anki version extras explosion

## Summary

`pyproject.toml` has 14 near-identical optional-dependency groups (7 anki versions + 7 Qt version pairs) that differ only in version numbers. This is maintenance-heavy when adding new Anki versions.

## Current state

```toml
[project.optional-dependencies]
anki-2154 = ["aqt==2.1.54", "anki==2.1.54"]
anki-2165 = ["aqt==2.1.65", "anki==2.1.65"]
anki-2312 = ["aqt==23.12.1", "anki==23.12.1"]
# ... 4 more
qt6-2154 = ["PyQt6==6.3.1", ...]
qt6-2165 = ["PyQt6==6.5.0", ...]
# ... 5 more
```

Every new Anki release adds 2 new groups (anki + qt6), plus a qt5 group if applicable.

## Proposed solutions

### Option A: Constraint files per version

Move version pins to separate constraint files (e.g., `constraints/anki-2411.txt`) and reference them via `[tool.uv.sources]` or `constraint-dependencies`. The extras would just name the constraint to apply.

### Option B: Code generation script

Add a `scripts/generate-extras.py` that reads a versions matrix from a YAML/TOML file and writes the `[project.optional-dependencies]` section. Run as a pre-commit hook or manually on version bumps.

### Option C: Build-time resolution

Drop the per-version extras entirely and document that users should pin via `uv lock --upgrade-package aqt==x.y.z` or `pip install 'aqt==x.y.z'` alongside the plugin. Let the lockfile handle compatibility.

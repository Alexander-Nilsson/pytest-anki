# Version constraint files

Each file pins `anki`, `aqt`, and Qt bindings for a specific version
combination. Used in CI matrix entries and local development.

To install a specific version combination:

```bash
uv sync --group dev \
  --extra anki-2411 \
  --extra qt6-2411 \
  --constraint constraints/anki-2411.txt
```

When adding a new Anki version:

1. Create `anki-<version>.txt` with exact pins
2. Add extras group in `pyproject.toml`
3. Add CI matrix entry in `.github/workflows/general.yml`

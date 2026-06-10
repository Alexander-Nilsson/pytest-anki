# Public type stubs for downstream users

## Summary

The public API (`pytest_anki/plugin.py` and `pytest_anki/__init__.py` re-export from `_plugin/` which is private by convention. Downstream users get poor IDE autocompletion and type-checking because the public surface doesn't carry explicit type signatures.

## Current state

`pytest_anki/plugin.py` re-exports:

```python
from ._plugin.launch import anki_running
from ._plugin.session import AnkiSession
```

But `AnkiSession`'s full API (properties, context managers, type params) isn't re-exported with typed stubs. `AnkiStateUpdate` is similarly opaque.

## What's needed

Either:

### Option A: py.typed marker + explicit re-exports

Add `py.typed` marker file and ensure the public `__init__.py` explicitly re-exports all types users need:

```python
from ._plugin.anki import AnkiStateUpdate
from ._plugin.session import AnkiSession
from ._plugin.types import PathLike
```

### Option B: Dedicated stubs

Add `pytest_anki/plugin.pyi` stub files that mirror the public API with full type signatures.

### Option C: Move public types out of _plugin

Promote `AnkiSession`, `AnkiStateUpdate`, `AnkiWebViewType` to `pytest_anki/` directly (re-exporting from `_plugin/` implementations).

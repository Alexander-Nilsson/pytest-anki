# Non-forked process resilience

## Summary

When `--anki-no-fork` is used (or `pytest-forked` is unavailable), module-level state from addons leaks between tests. The `loaded_addon` context manager handles `sys.modules` cleanup, but not monkey-patches on `aqt` objects.

## Current behaviour

With `--anki-no-fork`, tests share a single Python process. An addon that does:

```python
from aqt import gui_hooks
gui_hooks.reviewer_did_show_question.append(my_hook)
```

leaves that hook registered for subsequent tests. The plugin cleans up `gui_hooks.profile_did_open._hooks` and `anki.hooks._hooks` after each session, but not all hook registries.

## Proposed solution

Provide a utility or context manager for addons to self-clean, or implement a more comprehensive hook snapshot/restore mechanism in the session teardown that covers all `gui_hooks` registries.

## Alternative

Document that users should always use `loaded_addon` context manager, and enhance it to:

1. Snapshot all `gui_hooks` registries before import
2. Restore them on exit
3. Optionally snapshot and restore `aqt` module-level attributes

## Related

- `pytest_anki/_plugin/launch.py` lines 331-336 (partial hook restoration already exists)

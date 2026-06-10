# Lightweight session mode

## Summary

Every invocation of the `anki_session` fixture creates a full temporary directory, initializes a ProfileManager, creates a user profile, and (optionally) loads a collection. For suites with many parameterized tests or quick smoke tests, this overhead adds up.

## Use case

```python
# 15 parameterized configs, each spins up a full Anki session:
@pytest.mark.parametrize("anki_session", [
    dict(addon_configs=[("my_addon", {"key": v})])
    for v in range(15)
], indirect=True)
def test_config_variations(anki_session):
    ...
```

Each iteration pays the full cost of `base_directory()` + `temporary_user()` + Anki `_run()`.

## Proposed solution

Add a `shared_session` or `quick_session` fixture that:

1. Starts Anki once per session (or module)
2. Resets state between tests (unload profile, clear addons, reset configs) instead of restarting
3. Flagged as a session-scoped fixture with a state-reset protocol

## Design considerations

- Must still fork or isolate state per test (compose with existing `--anki-no-fork` logic)
- Profile reset is cheaper than full teardown/setup
- Selenium/web-debugging tests would still need full sessions
- Should be opt-in, not default (full isolation is safer)

## Prior art

- Django's `django.test.TestCase` vs `TransactionTestCase` — lighter isolation for faster runs
- pytest-django's `db` marker — reusable database between tests

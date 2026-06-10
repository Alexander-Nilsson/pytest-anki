# Dedicated fixture marker/decorator for anki_session parameters

## Summary

The `anki_session` fixture currently requires `@pytest.mark.parametrize("anki_session", [dict(...)], indirect=True)` to pass parameters. This is verbose, non-obvious, and requires users to understand pytest indirect parametrization.

## Current API

```python
@pytest.mark.parametrize("anki_session", [
    dict(unpacked_addons=[("my_addon", "/path/to/addon")]),
], indirect=True)
def test_something(anki_session):
    ...
```

## Proposed API

A dedicated marker or decorator:

```python
@pytest.mark.anki_session(unpacked_addons=[("my_addon", "/path/to/addon")])
def test_something(anki_session):
    ...
```

Or a decorator form:

```python
@anki_session_params(unpacked_addons=[("my_addon", "/path/to/addon")])
def test_something(anki_session):
    ...
```

## Benefits

- More discoverable (autocomplete on `@pytest.mark.anki_session`)
- Less boilerplate
- No need to understand pytest indirect parametrization
- Can provide IDE-level validation of parameter keys

## Implementation notes

Would need a pytest marker registered in `pytest_configure` and a hook in `pytest_fixture_post_finalizer` or similar to extract marker args into `request.param`.

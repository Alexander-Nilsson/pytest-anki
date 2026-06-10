# Local testability — Docker workflow / test-light mode

## Summary

The test suite cannot run locally due to Qt6 WebEngine requiring `libxml2.so.2` with a specific ABI unavailable on the developer's machine (Arch Linux with system Python). Currently, full validation requires CI (Ubuntu 24.04).

## Problems

1. High friction for development — every change must be pushed to CI to verify
2. New contributors face the same barrier
3. Debugging test failures is slow

## Proposed solutions

### Option A: Document Docker workflow

Provide a `docker-compose.yml` or `Makefile` target that mirrors the CI environment:

```makefile
.PHONY: test-docker
test-docker:
	docker run --rm \
		-e QT_QPA_PLATFORM=offscreen \
		-v $(PWD):/app \
		-w /app \
		ghcr.io/actions/ubuntu-24.04:latest \
		bash -c "uv sync --group dev --extra anki-2411 --extra qt6-2411 && uv run pytest -n4 tests/ -p no:xvfb"
```

### Option B: test-light mode

Introduce a `PYTEST_ANKI_TEST_LIGHT=1` env var that skips WebEngine-dependent tests and uses `QT_QPA_PLATFORM=offscreen` automatically. This wouldn't test Selenium or webview features, but would cover all core logic (fixtures, addon loading, config, subprocess, hooks).

### Option C: Pre-built CI Docker image

Publish a CI Docker image with the correct ABI so developers can pull and test locally without setting up Qt6 on their host.

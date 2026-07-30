SHELL = /bin/bash

PACKAGE_FOLDER = pytest_anki
TESTS_FOLDER = tests
MONITORED_FOLDERS = $(PACKAGE_FOLDER) $(TESTS_FOLDER)
TEST_FLAGS ?= -n4

# Set up project
install:
	uv sync --only-group dev --extra anki-2154 --extra qt5-2154

# ── Full suite (uv run — validates against locked deps) ──────────────────

# Run full test suite
test:
	uv run pytest $(TEST_FLAGS) tests/

# Run type checker
check:
	uv run ty check

# Run code linters
lint:
	uv run ruff check $(MONITORED_FOLDERS)
	uv run ruff format --check $(MONITORED_FOLDERS)

pre-commit:
	uv run pre-commit run --all-files --show-diff-on-failure

format:
	uv run ruff check --fix $(MONITORED_FOLDERS)
	uv run ruff format $(MONITORED_FOLDERS)

# ── Local dev targets (uvx — fast feedback, unconstrained) ───────────────

test-fast:
	uvx pytest tests/test_anki_unit.py

lint-fast:
	uvx ruff check $(MONITORED_FOLDERS)

format-fast:
	uvx ruff format $(MONITORED_FOLDERS)

check-fast:
	uvx ty check

# Run tests in Docker (Ubuntu 24.04, matches CI environment)
test-docker:
	docker compose run --rm test

# Run tests in headless mode without WebEngine-dependent tests
test-light:
	PYTEST_ANKI_TEST_LIGHT=1 QT_QPA_PLATFORM=offscreen python -m pytest $(TEST_FLAGS) tests/ -p no:xvfb -k "not web_debugging"

# Build project
build:
	uv build
help:
	@echo "$$(tput bold)Available targets:$$(tput sgr0)";echo;sed -ne"/^# /{h;s/.*//;:d" -e"H;n;s/^# //;td" -e"s/:.*//;G;s/\\n# /---/;s/\\n/ /g;p;}" ${MAKEFILE_LIST}|LC_ALL='C' sort -f|awk -F --- -v n=$$(tput cols) -v i=19 -v a="$$(tput setaf 6)" -v z="$$(tput sgr0)" '{printf"%s%*s%s ",a,-i,$$1,z;m=split($$2,w," ");l=n-i;for(j=1;j<=m;j++){l-=length(w[j])+1;if(l<= 0){l=n-i-length(w[j])-1;printf"\n%*s ",-i," ";}printf"%s ",w[j];}printf"\n";}'

.DEFAULT_GOAL: help
.PHONY: install test build check lint format test-fast lint-fast format-fast check-fast

import subprocess
from unittest.mock import patch

import pytest

from pytest_anki._plugin.subprocess import _parse_last_json_line, run_in_subprocess


class TestParseLastJsonLine:
    def test_simple_json(self):
        result = _parse_last_json_line('{"status": "passed"}')
        assert result == {"status": "passed"}

    def test_last_line_wins(self):
        text = "some output\n{\"status\": \"first\"}\n{\"status\": \"second\"}"
        result = _parse_last_json_line(text)
        assert result == {"status": "second"}

    def test_ignores_non_json_lines(self):
        text = "line1\nnot json\n{\"status\": \"ok\"}"
        result = _parse_last_json_line(text)
        assert result == {"status": "ok"}

    def test_ignores_invalid_json(self):
        text = "line1\n{invalid}"
        result = _parse_last_json_line(text)
        assert result is None

    def test_no_json_at_all(self):
        text = "just text\nmore text"
        result = _parse_last_json_line(text)
        assert result is None

    def test_empty_string(self):
        assert _parse_last_json_line("") is None

    def test_trailing_newlines(self):
        text = "prefix\n{\"key\": \"value\"}\n\n"
        result = _parse_last_json_line(text)
        assert result == {"key": "value"}


class TestRunInSubprocessErrors:
    def test_timeout(self):
        with patch(
            "pytest_anki._plugin.subprocess.subprocess.run"
        ) as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="python", timeout=60
            )
            result = run_in_subprocess("pass", timeout=60)
            assert result["status"] == "timeout"
            assert "timed out" in result["message"]

    def test_invocation_error(self):
        with patch(
            "pytest_anki._plugin.subprocess.subprocess.run"
        ) as mock_run:
            mock_run.side_effect = FileNotFoundError("python not found")
            result = run_in_subprocess("pass")
            assert result["status"] == "error"
            assert "Subprocess invocation failed" in result["message"]

    def test_unparseable_output(self):
        with patch(
            "pytest_anki._plugin.subprocess.subprocess.run"
        ) as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["python"], returncode=0, stdout="not json", stderr=""
            )
            result = run_in_subprocess("pass")
            assert result["status"] == "error"
            assert "Could not parse subprocess output" in result["message"]

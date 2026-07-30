# pytest-anki
#
# Copyright (C)  2026 Alexander Nilsson
# Copyright (C)  2019-2025 Aristotelis P. <https://glutanimate.com/>
#                and contributors (see CONTRIBUTORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/>.

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, Dict, Optional


def run_in_subprocess(
    body_source: str,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """Run test code in a fresh subprocess with isolated env vars.

    Sets the given env vars (including QTWEBENGINE_REMOTE_DEBUGGING) before
    any Qt imports, then provides a standalone QtBot (``_qtbot``) supporting
    ``wait_signal`` and ``wait_until``.

    The *body_source* is indented into a ``_run_test()`` function and wrapped
    with error handling. The last line of stdout should be a JSON dict with at
    least a ``"status"`` key (``"passed"``, ``"skipped"``, or ``"failed"``).

    Returns a dict with keys ``status``, ``message`` (optional),
    ``stderr`` / ``stdout`` (truncated on failure).
    """
    if env is None:
        env = {}
    env_assignments = "\n".join(
        "os.environ[{}] = {}".format(json.dumps(k), json.dumps(v))
        for k, v in env.items()
    )

    _project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    full_code = (
        "import os, sys, json\n"
        + env_assignments
        + "\n"
        + "sys.path.insert(0, {})\n".format(json.dumps(_project_root))
        + "try:\n"
        + "    from pytest_anki._plugin.qtbot import _qtbot, StandaloneQtBot\n"
        + "\n"
        + "    def _run_test():\n"
        + textwrap.indent(body_source, "        ")
        + "\n"
        + "    _run_test()\n"
        + "except SystemExit:\n"
        + "    raise\n"
        + "except BaseException:\n"
        + "    import traceback\n"
        + "    _tb = traceback.format_exc()\n"
        + "    sys.stderr.write(_tb)\n"
        + "    print(json.dumps({'status': 'failed', 'message': _tb}))\n"
        + "    sys.exit(1)\n"
    )

    result: Dict[str, Any]
    fd, script_path = tempfile.mkstemp(suffix=".py", prefix="pytest_anki_web_")
    with os.fdopen(fd, "w") as f:
        f.write(full_code)

    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        result = {
            "status": "timeout",
            "message": "Subprocess timed out after {}s".format(timeout),
        }
        return result
    except Exception as e:
        result = {
            "status": "error",
            "message": "Subprocess invocation failed: {}".format(e),
        }
        return result
    finally:
        if os.path.exists(script_path):
            os.unlink(script_path)

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    # Parse the last JSON line from stdout
    parsed = _parse_last_json_line(stdout)

    if parsed is None:
        result = {
            "status": "error",
            "message": "Could not parse subprocess output",
            "stdout": stdout[:2000],
            "stderr": stderr[:2000],
        }
    else:
        result = parsed

    # Attach diagnostics on failure
    if result.get("status") in ("error", "failed", "timeout"):
        result.setdefault("stderr", stderr[:3000])
        result.setdefault("stdout", stdout[:2000])

    return result


def _parse_last_json_line(text: str) -> Optional[Dict[str, Any]]:
    for line in reversed(text.strip().split("\n")):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None

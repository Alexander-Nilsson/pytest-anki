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
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

import time
from unittest.mock import Mock

import pytest

from pytest_anki import AnkiSession, AnkiSessionError, AnkiWebViewType
from pytest_anki._plugin.subprocess import run_in_subprocess

_WEB_DEBUGGING_AVAILABLE_BODY = r"""
import requests
from pytest_anki._plugin.launch import anki_running

with anki_running(qtbot=_qtbot, enable_web_debugging=True) as session:
    port = session.web_debugging_port

    def assert_web_debugging_interface_up():
        result = requests.get(f"http://127.0.0.1:{port}/")
        assert result.status_code == 200
        assert "Inspectable pages" in result.text

    session.run_in_thread_and_wait(assert_web_debugging_interface_up)

print(json.dumps({"status": "passed"}))
"""

_WEB_DRIVER_CONNECT_BODY = r"""
try:
    import selenium.webdriver
except ImportError:
    print(json.dumps({"status": "skipped", "reason": "selenium not installed"}))
    sys.exit(0)

from pytest_anki._plugin.launch import anki_running

with anki_running(qtbot=_qtbot, enable_web_debugging=True) as session:
    def assert_web_driver_connected(driver):
        assert driver.window_handles

    session.run_with_chrome_driver(assert_web_driver_connected)

print(json.dumps({"status": "passed"}))
"""

_WEB_DRIVER_SELECT_WEB_VIEW_BODY = r"""
try:
    import selenium.webdriver
except ImportError:
    print(json.dumps({"status": "skipped", "reason": "selenium not installed"}))
    sys.exit(0)

from pytest_anki import AnkiWebViewType
from pytest_anki._plugin.launch import anki_running

with anki_running(qtbot=_qtbot, enable_web_debugging=True) as session:
    def assert_web_driver_connected_to_main_web_view(driver):
        assert driver.title == AnkiWebViewType.main_webview.value

    with session.profile_loaded():
        session.run_with_chrome_driver(
            assert_web_driver_connected_to_main_web_view, AnkiWebViewType.main_webview
        )

print(json.dumps({"status": "passed"}))
"""

_WEB_DRIVER_INTERACT_BODY = r"""
try:
    import selenium.webdriver
except ImportError:
    print(json.dumps({"status": "skipped", "reason": "selenium not installed"}))
    sys.exit(0)

from pytest_anki import AnkiWebViewType
from pytest_anki._plugin.launch import anki_running

with anki_running(qtbot=_qtbot, enable_web_debugging=True) as session:
    def switch_to_deck_view(driver):
        driver.find_element("xpath", "//*[text()='Default']").click()

    with session.profile_loaded():
        assert session.mw.state == "deckBrowser"
        session.run_with_chrome_driver(
            switch_to_deck_view, AnkiWebViewType.main_webview
        )

        def mw_state_switched():
            assert session.mw.state == "overview"

        session.qtbot.wait_until(mw_state_switched)

print(json.dumps({"status": "passed"}))
"""


def _check_result(result):
    status = result.get("status")
    if status == "passed":
        return
    elif status == "skipped":
        pytest.skip(
            result.get(  # ty: ignore[too-many-positional-arguments]
                "reason", "Test skipped internally"
            )
        )
    elif status == "failed":
        message = result.get("message", "Test failed")
        stderr = result.get("stderr")
        if stderr:
            message += "\n--- stderr ---\n" + stderr
        pytest.fail(message)
    elif status == "timeout":
        pytest.fail("Test timed out: " + result.get("message", ""))
    elif status == "error":
        pytest.fail("Subprocess error: " + result.get("message", ""))
    else:
        pytest.fail("Unknown subprocess status: {}".format(result))


def test_run_in_thread(anki_session: AnkiSession):
    mock_task = Mock()
    args = tuple((1, 2, 3))
    kwargs = {"foo": 1, "bar": 2, "zing": 3}
    anki_session.run_in_thread_and_wait(
        task=mock_task, task_args=args, task_kwargs=kwargs
    )
    mock_task.assert_called_once_with(*args, **kwargs)


def test_can_supply_timeout(anki_session: AnkiSession):
    timeout_duration = 4
    task_duration = 3

    def mock_task():
        time.sleep(task_duration)

    start_time = time.time()
    try:
        anki_session.run_in_thread_and_wait(
            task=mock_task, timeout=timeout_duration * 1000
        )
    except AnkiSessionError:
        pytest.fail("Call unexpectedly timed out")  # ty: ignore[invalid-argument-type]

    wait_time = time.time() - start_time

    assert timeout_duration > wait_time >= task_duration

    with pytest.raises(AnkiSessionError):
        anki_session.run_in_thread_and_wait(
            task=mock_task, timeout=(task_duration - 1) * 1000
        )


def test_web_debugging_available_on_launch():
    result = run_in_subprocess(
        _WEB_DEBUGGING_AVAILABLE_BODY,
        env={"QTWEBENGINE_REMOTE_DEBUGGING": "1"},
    )
    _check_result(result)


def test_web_driver_can_connect():
    result = run_in_subprocess(
        _WEB_DRIVER_CONNECT_BODY,
        env={"QTWEBENGINE_REMOTE_DEBUGGING": "1"},
    )
    _check_result(result)


def test_web_driver_can_select_web_view():
    result = run_in_subprocess(
        _WEB_DRIVER_SELECT_WEB_VIEW_BODY,
        env={"QTWEBENGINE_REMOTE_DEBUGGING": "1"},
    )
    _check_result(result)


def test_web_driver_can_interact_with_anki():
    result = run_in_subprocess(
        _WEB_DRIVER_INTERACT_BODY,
        env={"QTWEBENGINE_REMOTE_DEBUGGING": "1"},
    )
    _check_result(result)


@pytest.mark.env({"QTWEBENGINE_REMOTE_DEBUGGING": "12345"})
@pytest.mark.parametrize(
    "anki_session",
    [
        dict(
            enable_web_debugging=False,
        )
    ],
    indirect=True,
)
def test_web_debugging_can_be_disabled_even_when_port_set(anki_session: AnkiSession):
    assert anki_session.web_debugging_port is None

    with pytest.raises(AnkiSessionError) as exception_info:
        anki_session.run_with_chrome_driver(
            lambda driver: None, AnkiWebViewType.main_webview
        )

    assert str(exception_info.value) == "Web debugging interface is not active"

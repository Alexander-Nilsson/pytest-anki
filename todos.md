
Right now, `pytest-anki` handles headless sessions and profile mocking beautifully, but its UI/Webview testing support is practically non-existent or fragile.

Here is an engineering blueprint of features, improvements, and fixes you can natively implement inside your `pytest-anki` library repository to turn it into a world-class UI testing companion.

---

### 1. Robust Engine Isolation (Fix the 5-second timeout)

When running consecutive tests, Qt WebEngine often keeps child processes or socket bindings alive for a few moments after Anki shuts down. This causes the next test's `anki_session` setup to hang or time out.

**What to implement in `pytest-anki`:**

* Update the session manager teardown routine to proactively kill lingering child processes.
* Add an automatic "Port Scanner" feature that assigns a random, free port to `QTWEBENGINE_REMOTE_DEBUGGING` for every unique session, preventing port collisions if tests run rapidly or in parallel via `pytest-xdist`.

### 2. Introduce a Built-in Direct Webview API

Instead of forcing the user to implement their own custom WebSocket connection wrappers or install Playwright/Selenium, build a lightweight async CDP connection engine directly into `pytest-anki`'s core `AnkiSession` object.

**What to implement in `pytest-anki`:**
Add a native method or property to `AnkiSession` like `.webview_driver` that handles the direct WebSocket handshake completely behind the scenes.

```python
# What an addon developer's test would look like using your updated library:
def test_editor_addon(anki_session: AnkiSession):
    with anki_session.profile_loaded():
        # Open a specific web view panel
        editor = anki_session.open_editor() 
        
        # Pull your library's native, lightweight CDP driver 
        driver = anki_session.get_webview_driver(target_hint="editor")
        
        # High-level methods you built into the library
        driver.fill("#fields-0", "Card front content")
        assert "Card front" in driver.get_text("#fields-0")

```

### 3. Expose Smart "Anki-Aware" Waiting Helpers

Because you are building the library specifically for Anki, you can create smart waiting helpers that raw tools can't do natively. For instance, waiting until a specific Anki-specific field or layout component has finished rendering over the bridge.

**What to implement in `pytest-anki`:**
Inside your custom webview driver helper class, bundle an elegant polling retry utility to mimic Playwright's auto-waiting features without pulling in the heavy framework dependency:

```python
# Internal method inside your library's custom driver class
def wait_for_selector(self, selector, timeout=5.0):
    import time
    start = time.time()
    while time.time() - start < timeout:
        res = self.evaluate_js(f"!!document.querySelector('{selector}')")
        if res.get('value') is True:
            return True
        time.sleep(0.1)
    raise TimeoutError(f"Selector '{selector}' did not appear within {timeout}s")

```

### 4. Provide Native Web Inspector Hooks

When a headless UI test fails, it is an absolute nightmare to debug because you can't see what the Qt WebEngine window looked like at the moment of failure.

**What to implement in `pytest-anki`:**

* **`anki_session.save_webview_html(selector)`**: A helper method that dumps the exact current DOM structure of a webview to a file in the `.pytest_cache` or a target log directory upon a test failure.
* **Console Log Forwarding**: Use the CDP `Log.enable` and `Runtime.enable` methods to intercept console logs, warnings, and errors originating inside Anki's editor or reviewer webviews and bubble them straight up into the standard `pytest` stdout log output.

---

### Suggested TODO Checklists for your `pytest-anki` Repository

You can manage this roadmap in your library repo by breaking it into these distinct features:

* [ ] **Feature: Dynamic Debug Port Mapping**
* [ ] Modify `AnkiSession` startup environment variables to find and assign a random available high-range port for `QTWEBENGINE_REMOTE_DEBUGGING`.
* [ ] Implement aggressive socket cleanup on fixture teardown to prevent port-binding exhaustion.


* [ ] **Feature: Embedded CDP Client Core**
* [ ] Integrate a clean async HTTP/WebSocket connector (e.g., using Python's lightweight standard library extensions or adding a minimal explicit dependency like `aiohttp`).
* [ ] Implement a `TargetResolver` utility inside the session module that targets `/json` and parses out tabs (`editor`, `reviewer`, `deckbrowser`).


* [ ] **Feature: Fluent UI Interactions**
* [ ] Create wrapper methods on the session class for common actions: `click_element(selector)`, `set_input_value(selector, text)`, and `get_element_html(selector)`.
* [ ] Implement a safe `wait_for_element()` retry loop framework.


* [ ] **Feature: Test Observability & Debugging**
* [ ] Build a hook that captures webview DOM states and surfaces console errors into the pytest report if a test fails.

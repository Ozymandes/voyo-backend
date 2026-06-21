"""
Pytest fixtures for the VOYO Playwright e2e suite.

Two non-obvious Flutter-web requirements solved here:
1. SEMANTICS ACTIVATION — Flutter web does not expose its accessibility tree
   until a keyboard interaction occurs. We send Tab keypresses + a click to
   force the tree to build, otherwise get_by_role() finds nothing.
2. AUTHENTICATION — the app gates on a Supabase email/password login. We log
   in once per session (in a shared browser context so localStorage/cookies
   persist), then each test opens a fresh page that inherits the authed
   session and lands directly on the Explore screen.

Credentials come from env vars VOYO_TEST_EMAIL / VOYO_TEST_PASSWORD (in .env,
gitignored). The suite is skipped cleanly if either is missing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Load .env so VOYO_TEST_EMAIL / VOYO_TEST_PASSWORD are available without
# manual export. conftest is imported before any test, so this covers all.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pytest

pytest_plugins = []
pw = pytest.importorskip("playwright", reason="playwright not installed: "
                         "pip install playwright && python -m playwright install chromium")

BASE_URL = os.environ.get("VOYO_WEB_URL", "http://localhost:8099")
RESPONSE_TIMEOUT_MS = int(os.environ.get("VOYO_E2E_TIMEOUT_MS", "30000"))
FLUTTER_BOOT_MS = int(os.environ.get("VOYO_FLUTTER_BOOT_MS", "15000"))


def _activate_semantics(page) -> None:
    """Force Flutter web to build its semantic tree.

    Flutter web lazily builds accessibility nodes on the first keyboard
    interaction. Without this, get_by_role / get_by_text find nothing even
    though the app is fully rendered on the canvas.
    """
    page.evaluate("() => { document.body.focus(); }")
    for _ in range(25):
        page.keyboard.press("Tab")
        page.wait_for_timeout(120)
    page.wait_for_timeout(1000)
    # a pointer event on the canvas kicks the engine into interactive mode
    page.mouse.click(640, 450)
    page.wait_for_timeout(2000)
    for _ in range(10):
        page.keyboard.press("Tab")
        page.wait_for_timeout(120)
    page.wait_for_timeout(2000)


def _do_login(page) -> None:
    """Fill the login form via keyboard events + submit.

    Flutter web textboxes are semantic nodes, not real <input> elements, so
    Playwright's fill() (which synthesizes a paste) is ignored. We must
    click() to focus then press_sequentially() to type char-by-char — Flutter
    listens to keyboard events on its TextField controller.
    """
    email = os.environ.get("VOYO_TEST_EMAIL", "")
    password = os.environ.get("VOYO_TEST_PASSWORD", "")
    if not email or not password:
        pytest.skip("VOYO_TEST_EMAIL / VOYO_TEST_PASSWORD not set — see .env")

    email_tb = page.get_by_role("textbox", name="email").first
    pw_tb = page.get_by_role("textbox", name="password").first
    email_tb.click()
    page.wait_for_timeout(200)
    email_tb.press_sequentially(email, delay=25)
    pw_tb.click()
    page.wait_for_timeout(200)
    pw_tb.press_sequentially(password, delay=25)
    page.wait_for_timeout(500)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    # auth round-trip + Flutter navigation to Explore
    page.wait_for_timeout(12000)


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Generous viewport so the desktop layout (the demo target) renders."""
    return {**browser_context_args,
            "viewport": {"width": 1280, "height": 900}}


@pytest.fixture(scope="session")
def authed_context(browser, browser_context_args):
    """Log in once per session. The browser context (with its localStorage
    holding the Supabase session) is shared across all tests so each one
    opens a fresh page that inherits the auth."""
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(FLUTTER_BOOT_MS)
    _activate_semantics(page)
    _do_login(page)
    # keep the context (auth persists in localStorage); drop the login page
    page.close()
    yield context
    context.close()


@pytest.fixture
def authenticated_page(authed_context, base_url):
    """A fresh page in the authed context. Lands on Explore (Flutter sees
    the Supabase session in localStorage and skips the login screen)."""
    page = authed_context.new_page()
    page.goto(base_url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(FLUTTER_BOOT_MS)
    _activate_semantics(page)
    yield page
    page.close()


@pytest.fixture
def shot_dir():
    d = Path("data/evaluation/runs/e2e_screenshots")
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def response_timeout_ms() -> int:
    return RESPONSE_TIMEOUT_MS

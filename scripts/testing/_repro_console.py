"""Drive the map grey-box flow on :8099 and capture EVERY console / pageerror.

Goal: surface the REAL exception behind the
'Instance of DiagnosticsProperty<void>' storm (which is the wrapper, not
the cause). Prints all console + pageerror events with full text + stack.
"""
import sys, os, json
sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv('.env')
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("VOYO_TEST_EMAIL", "")
PASSWORD = os.environ.get("VOYO_TEST_PASSWORD", "")
URL = "http://localhost:8099"

events = {"log": [], "error": [], "warning": [], "info": [], "pageerror": []}


def dump_events(label):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    print(f"  log={len(events['log'])} error={len(events['error'])} "
          f"warning={len(events['warning'])} pageerror={len(events['pageerror'])}")
    seen = set()
    for kind in ["pageerror", "error", "warning"]:
        for e in events[kind]:
            key = (kind, e[:200])
            if key in seen:
                continue
            seen.add(key)
            print(f"\n  [{kind}] {e[:500]}")


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1280, "height": 900})

    def on_console(msg):
        t = msg.type
        if t not in events:
            events[t] = []
        events[t].append(msg.text)
        if "DiagnosticsProperty" in msg.text:
            print(f"  STORM-SIG: {msg.text[:160]}")

    def on_pageerror(err):
        events["pageerror"].append(f"{err.message}\n--- stack ---\n{err.stack}")

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)

    print(f"> goto {URL}")
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(18000)
    dump_events("after app boot (pre-login)")

    print("\n> activate Flutter web semantics")
    page.evaluate("() => { document.body.focus(); }")
    for _ in range(25):
        page.keyboard.press("Tab")
        page.wait_for_timeout(120)
    page.wait_for_timeout(1000)
    page.mouse.click(640, 450)
    page.wait_for_timeout(2000)
    for _ in range(10):
        page.keyboard.press("Tab")
        page.wait_for_timeout(120)
    page.wait_for_timeout(2000)

    print("> login")
    page.get_by_role("textbox", name="email").first.click()
    page.get_by_role("textbox", name="email").first.press_sequentially(EMAIL, delay=20)
    page.get_by_role("textbox", name="password").first.click()
    page.get_by_role("textbox", name="password").first.press_sequentially(PASSWORD, delay=20)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    page.wait_for_timeout(15000)
    dump_events("after login (Explore map should be visible)")
    page.screenshot(path="work/_repro_01_map_loaded.png", full_page=True)

    print("\n> long-press Cairo center to trigger isochrone")
    page.mouse.move(640, 450)
    page.mouse.down()
    page.wait_for_timeout(900)
    page.mouse.up()
    page.wait_for_timeout(18000)
    page.screenshot(path="work/_repro_02_after_longpress.png", full_page=True)
    dump_events("after long-press (isochrone path)")

    body = page.inner_text("body")
    print(f"\n> body excerpt: {body[:300]!r}")

    print("\n> click map marker area (POI tap path)")
    for x, y in [(600, 400), (700, 380), (550, 460), (640, 350)]:
        page.mouse.click(x, y)
        page.wait_for_timeout(3500)
    page.screenshot(path="work/_repro_03_after_taps.png", full_page=True)
    dump_events("after marker taps (POI detail path)")

    b.close()

print("\n" + "=" * 70)
print("FULL CAPTURE COMPLETE")
print("=" * 70)

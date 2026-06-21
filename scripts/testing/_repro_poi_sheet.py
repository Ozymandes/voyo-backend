"""Reproduce the grey-block bug. Drive the app to open Egyptian Museum's POI sheet."""
import sys, os; sys.path.insert(0,'.')
from dotenv import load_dotenv; load_dotenv('.env')
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("VOYO_TEST_EMAIL", "")
PASSWORD = os.environ.get("VOYO_TEST_PASSWORD", "")
URL = "http://localhost:8099"

def activate(page):
    page.evaluate("() => { document.body.focus(); }")
    for _ in range(25): page.keyboard.press("Tab"); page.wait_for_timeout(120)
    page.wait_for_timeout(1000)
    page.mouse.click(640, 450)
    page.wait_for_timeout(2000)
    for _ in range(10): page.keyboard.press("Tab"); page.wait_for_timeout(120)
    page.wait_for_timeout(2000)

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width":1280,"height":900})
    # capture console logs
    page.on("console", lambda msg: print(f"  [CONSOLE {msg.type}] {msg.text[:200]}") if msg.type in ('error','warning') else None)
    page.on("pageerror", lambda err: print(f"  [PAGE ERROR] {str(err)[:300]}"))
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(20000)
    activate(page)
    # login
    page.get_by_role("textbox", name="email").first.click()
    page.get_by_role("textbox", name="email").first.press_sequentially(EMAIL, delay=20)
    page.get_by_role("textbox", name="password").first.click()
    page.get_by_role("textbox", name="password").first.press_sequentially(PASSWORD, delay=20)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    page.wait_for_timeout(15000)
    print("logged in. navigating to map...")
    # go to full map
    page.get_by_text("Full Map", exact=False).first.click()
    page.wait_for_timeout(8000)
    print("on map. looking for Egyptian Museum marker/stop...")
    body = page.inner_text("body").encode('ascii','replace').decode('ascii')
    if "Egyptian Museum" in body:
        print("  FOUND 'Egyptian Museum' text on map — tapping it")
        page.get_by_text("Egyptian Museum", exact=False).first.click()
        page.wait_for_timeout(4000)
        page.screenshot(path="work/_repro_egyptian_sheet.png", full_page=True)
        body2 = page.inner_text("body").encode('ascii','replace').decode('ascii')
        print(f"  after tap, body length: {len(body2)} chars")
        print(f"  body excerpt: {repr(body2[:500])}")
    else:
        print("  Egyptian Museum not visible on map — searching for any POI tap target")
        # try tapping a marker
        print(f"  body excerpt: {repr(body[:500])}")
    b.close()

"""Open a POI detail sheet from the Planner (list view, tappable via text)."""
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
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(20000)
    activate(page)
    page.get_by_role("textbox", name="email").first.click()
    page.get_by_role("textbox", name="email").first.press_sequentially(EMAIL, delay=20)
    page.get_by_role("textbox", name="password").first.click()
    page.get_by_role("textbox", name="password").first.press_sequentially(PASSWORD, delay=20)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    page.wait_for_timeout(15000)
    print("logged in, going to Planner...")
    page.get_by_text("Planner", exact=False).first.click()
    page.wait_for_timeout(5000)
    body = page.inner_text("body").encode('ascii','replace').decode('ascii')
    print(f"planner body excerpt: {repr(body[:600])}")
    # find a POI to tap
    for target in ["Egyptian Museum", "Khan el-Khalili", "Pyramid", "Citadel"]:
        if target in body:
            print(f"\n  tapping: {target}")
            page.get_by_text(target, exact=False).first.click()
            page.wait_for_timeout(5000)
            page.screenshot(path=f"work/_repro_planner_{target.lower().replace(' ','_')}.png", full_page=True)
            body2 = page.inner_text("body").encode('ascii','replace').decode('ascii')
            print(f"  after tap body length: {len(body2)}")
            print(f"  body excerpt: {repr(body2[:800])}")
            break
    b.close()

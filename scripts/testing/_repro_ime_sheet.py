"""Diagnostic: reproduce the IME POI tap on web to see what the SHARED
PoiDetailSheet widget actually renders. If grey appears here too → code/data
issue. If it renders fine → Windows-specific rendering bug.

Final fix verification will be on Windows; this is diagnosis only.
"""
import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv('.env')
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

EMAIL = os.environ.get("VOYO_TEST_EMAIL", "")
PASSWORD = os.environ.get("VOYO_TEST_PASSWORD", "")
URL = "http://localhost:8099"


def activate(page):
    page.evaluate("() => { document.body.focus(); }")
    for _ in range(25):
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
    page.wait_for_timeout(800)
    page.mouse.click(640, 450)
    page.wait_for_timeout(1500)
    for _ in range(10):
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
    page.wait_for_timeout(1500)


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1280, "height": 900})
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(16000)
    activate(page)
    page.get_by_role("textbox", name="email").first.click()
    page.get_by_role("textbox", name="email").first.press_sequentially(EMAIL, delay=15)
    page.get_by_role("textbox", name="password").first.click()
    page.get_by_role("textbox", name="password").first.press_sequentially(PASSWORD, delay=15)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    page.wait_for_timeout(12000)

    # We are now on the Explore screen (the IME). Find a POI list card and tap it.
    body = page.inner_text("body")
    print(f"on explore. body has 'Explore': {'Explore' in body}")
    print(f"body excerpt (ascii): {body[:200].encode('ascii','replace').decode()!r}")

    # Tap a POI name in the explore list (IME POI tap path)
    target = None
    for t in ["Khan el-Khalili", "Egyptian Museum", "Grand Egyptian", "Great Pyramid", "Citadel"]:
        if t in body:
            target = t
            break
    print(f"tapping IME POI: {target}")
    if target:
        page.get_by_text(target, exact=False).first.click()
        page.wait_for_timeout(6000)
        page.screenshot(path="work/_ime_sheet_web.png", full_page=True)
        # measure the sheet region
        arr = np.array(Image.open("work/_ime_sheet_web.png").convert("RGB"))
        h, w = arr.shape[:2]
        # the sheet covers bottom ~90% — sample its body (below the hero)
        sheet_body = arr[300:850, 50:1230]
        m = sheet_body.reshape(-1, 3).mean(axis=0).astype(int)
        # grey detection
        is_grey = (np.abs(sheet_body.astype(int).mean(axis=2) - int(m.mean())) < 8).mean() * 100
        uniq = len(np.unique((sheet_body[::6, ::6]).reshape(-1, 3), axis=0))
        print(f"\nIME sheet body region:")
        print(f"  mean RGB: {tuple(m)} = #{'%02x%02x%02x' % tuple(m)}")
        print(f"  flat-grey pixels: {is_grey:.1f}%  (high = uniform grey block)")
        print(f"  unique colors: {uniq}  (low = flat; high = real text/content)")
        # dump the sheet's visible text
        body2 = page.inner_text("body")
        print(f"\n  sheet text excerpt: {body2[:500].encode('ascii','replace').decode()!r}")
    b.close()

"""Diagnose why flutter_map tiles aren't painting on web.

Checks: (1) can the browser fetch a CartoDB tile? (2) what network
requests/responses happen for cartocdn? (3) is the map controller alive?
"""
import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv('.env')
from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("VOYO_TEST_EMAIL", "")
PASSWORD = os.environ.get("VOYO_TEST_PASSWORD", "")
URL = "http://localhost:8099"

carto_requests = []
carto_responses = []


def activate(page):
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


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1280, "height": 900})

    def on_request(req):
        if "cartocdn" in req.url or "tile" in req.url.lower():
            carto_requests.append((req.method, req.url[:120]))

    def on_response(resp):
        if "cartocdn" in resp.url or "tile" in resp.url.lower():
            carto_responses.append((resp.status, resp.url[:120]))

    page.on("request", on_request)
    page.on("response", on_response)

    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(15000)
    activate(page)

    # Login
    page.get_by_role("textbox", name="email").first.click()
    page.get_by_role("textbox", name="email").first.press_sequentially(EMAIL, delay=20)
    page.get_by_role("textbox", name="password").first.click()
    page.get_by_role("textbox", name="password").first.press_sequentially(PASSWORD, delay=20)
    page.get_by_role("button").filter(has_text="Sign In").first.click()
    page.wait_for_timeout(12000)

    print(f"cartocdn requests seen during login: {len(carto_requests)}")
    print(f"cartocdn responses seen: {len(carto_responses)}")
    for s, u in carto_responses[:5]:
        print(f"  HTTP {s}: {u}")

    # Wait for map to attempt tile loading
    page.wait_for_timeout(8000)
    print(f"\nafter wait — cartocdn requests: {len(carto_requests)}, responses: {len(carto_responses)}")

    # Direct fetch test from browser context
    print("\n=== direct browser fetch test ===")
    result = page.evaluate("""async () => {
        const outcomes = [];
        const urls = [
            'https://a.basemaps.cartocdn.com/rastertiles/voyager/12/1543/1417.png',
            'https://tile.openstreetmap.org/12/1543/1417.png'
        ];
        for (const url of urls) {
            try {
                const r = await fetch(url);
                const blob = await r.blob();
                outcomes.push({url: url.split('/')[2], status: r.status, type: blob.type, size: blob.size});
            } catch (e) {
                outcomes.push({url: url.split('/')[2], error: e.message});
            }
        }
        return outcomes;
    }""")
    for o in result:
        print(f"  {o}")

    # Check if flutter_map's internal image loading threw any errors we can see
    print("\n=== pan the map (trigger tile fetch for new viewport) ===")
    before = len(carto_requests)
    # Drag the map
    page.mouse.move(640, 450)
    page.mouse.down()
    page.mouse.move(500, 400, steps=8)
    page.mouse.up()
    page.wait_for_timeout(6000)
    print(f"new cartocdn requests after pan: {len(carto_requests) - before}")

    # Screenshot the result
    page.screenshot(path="work/_repro_04_after_pan.png", full_page=True)
    print("screenshot: work/_repro_04_after_pan.png")

    b.close()

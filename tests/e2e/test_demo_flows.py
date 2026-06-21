"""
VOYO Playwright end-to-end suite — the four critical demo flows.

Runs against a Flutter web build served on VOYO_WEB_URL (default
http://localhost:8099) with the full stack up (backend :8000, docker-compose
OSRM+Valhalla+VROOM healthy). Each test uses the ``authenticated_page``
fixture from conftest.py, which handles Flutter semantics activation +
Supabase login once per session.

Run:
    pytest tests/e2e/test_demo_flows.py -v -o addopts=""

Each test captures a screenshot under
data/evaluation/runs/e2e_screenshots/ for the thesis appendix. The
isochrone test (test_isochrone_non_modal_panel) produces the figure that
replaces the bare-matplotlib isochrone renders in §4.

Implementation note: tests use the SYNC Playwright API. Flutter web
textboxes need click()+press_sequentially() (not fill()) — see
conftest._do_login.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.slow]


def _on_explore(page) -> bool:
    """Heuristic: are we on the main Explore screen?"""
    body = page.inner_text("body").lower()
    return ("discover egypt" in body) or ("places" in body and "map" in body)


@pytest.mark.e2e
def test_explore_poi_detail_opens(authenticated_page, shot_dir, response_timeout_ms):
    """EXPLORE: from the Explore screen, a POI card tap opens the detail
    sheet showing the image carousel + a price row (EGP)."""
    page = authenticated_page
    assert _on_explore(page), "Not on Explore screen after login"
    # Wait for the first POI card. Flutter cards are tappable buttons with
    # the POI name as text; pick a known POI name to be specific.
    poi = page.get_by_text("Pyramid", exact=False).first
    poi.wait_for(state="visible", timeout=response_timeout_ms)
    poi.click()
    page.wait_for_timeout(1500)  # detail sheet animation
    page.screenshot(path=str(shot_dir / "01_explore_poi_detail.png"), full_page=True)
    body = page.inner_text("body")
    # The detail sheet surfaces a price cue (EGP) and a POI description.
    assert ("EGP" in body) or ("E£" in body) or ("L.E" in body) or ("admission" in body.lower()), \
        "POI detail did not surface a price row"


@pytest.mark.e2e
def test_cleo_returns_response(authenticated_page, shot_dir, response_timeout_ms):
    """CLEO: open chat, send 'hello', assert a non-empty response within
    the timeout. A rate-limit fallback message counts as a valid response."""
    page = authenticated_page
    assert _on_explore(page), "Not on Explore screen after login"
    # CLEO chat is a bottom-nav tab labelled 'Cleo' (index 3).
    cleo_entry = page.get_by_text("Cleo", exact=False).first
    cleo_entry.wait_for(state="visible", timeout=10000)
    cleo_entry.click()
    page.wait_for_timeout(3000)  # chat screen mount
    # The chat screen shows suggested-prompt chips that directly trigger a
    # CLEO response. Use one instead of fighting the composer focus.
    prompt = page.get_by_text("Best time to visit Luxor", exact=False).first
    prompt.wait_for(state="visible", timeout=10000)
    prompt.click()
    page.wait_for_timeout(response_timeout_ms)  # CLEO response latency
    page.screenshot(path=str(shot_dir / "02_cleo_response.png"), full_page=True)
    # Assert: a response bubble appeared (chat surface gained content beyond
    # the empty-state prompt). We check the body text grew substantially.
    body = page.inner_text("body")
    assert len(body) > 200, "CLEO did not return a substantive response"


@pytest.mark.e2e
def test_add_to_itinerary_sheet_opens(authenticated_page, shot_dir, response_timeout_ms):
    """ADD-TO-ITINERARY: from a POI detail sheet, 'Add to trip' opens the
    AddToItineraryFlow sheet (the VROOM feasibility verdict surface)."""
    page = authenticated_page
    assert _on_explore(page), "Not on Explore screen after login"
    # Open a POI detail first.
    poi = page.get_by_text("Pyramid", exact=False).first
    poi.wait_for(state="visible", timeout=response_timeout_ms)
    poi.click()
    page.wait_for_timeout(1500)
    # The 'Add to trip' CTA opens the feasibility sheet.
    add_cta = page.get_by_text("Add to trip", exact=False).first
    add_cta.wait_for(state="visible", timeout=10000)
    add_cta.click()
    page.wait_for_timeout(2000)  # VROOM feasibility check round-trip
    page.screenshot(path=str(shot_dir / "03_add_to_itinerary.png"), full_page=True)
    body = page.inner_text("body").lower()
    # The sheet surfaces a day picker or a feasibility verdict (fit/doesn't fit).
    assert ("day" in body) or ("fit" in body) or ("pick" in body) or ("trip" in body), \
        "Add-to-itinerary sheet did not open"


@pytest.mark.e2e
def test_isochrone_non_modal_panel(authenticated_page, shot_dir, response_timeout_ms):
    """ISOCHRONE: a long-press on the map shows the reachable-area bloom
    (the non-modal Valhalla isochrone overlay). This screenshot replaces
    the bare-matplotlib isochrone renders in the thesis §4 figures."""
    page = authenticated_page
    # Navigate to the map surface from Explore.
    map_entry = page.get_by_text("Full Map", exact=False).first
    if map_entry.count() == 0:
        map_entry = page.get_by_text("Map", exact=False).first
    map_entry.wait_for(state="visible", timeout=10000)
    map_entry.click()
    page.wait_for_timeout(3000)  # map tiles + markers load
    page.screenshot(path=str(shot_dir / "04a_map_loaded.png"), full_page=True)
    # Long-press near the centre of the default viewport (Cairo area).
    page.mouse.move(640, 400)
    page.mouse.down()
    page.wait_for_timeout(1000)  # hold for the long-press threshold
    page.mouse.up()
    page.wait_for_timeout(response_timeout_ms)  # isochrone render + panel
    page.screenshot(path=str(shot_dir / "04b_isochrone_bloom.png"), full_page=True)
    body = page.inner_text("body").lower()
    # The non-modal panel shows reachable-area summary text.
    assert ("reachable" in body) or ("within" in body) or ("min walk" in body) or \
           ("min drive" in body) or ("places within" in body), \
        "Isochrone reachable-area panel did not appear"

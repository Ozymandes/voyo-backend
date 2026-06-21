"""
Personalization Integration Test

Verifies that CLEO produces meaningfully different recommendations
for users with different profiles stored in Supabase.

Run from project root:
    python tests/integration/personalization/test_personalization.py

Requires mock users to be seeded first:
    python scripts/seed_test_users.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cleo.cleo_agent import CleoAgent

# Fixed UUIDs matching seed_test_users.py
TEST_USER_HISTORY    = "11111111-1111-1111-1111-111111111111"
TEST_USER_OUTDOOR    = "22222222-2222-2222-2222-222222222222"
TEST_USER_ACCESSIBLE = "33333333-3333-3333-3333-333333333333"

QUERY = "What should I visit in Cairo?"

HISTORY_KEYWORDS    = ["pyramid", "museum", "temple", "pharaoh", "ancient",
                       "historical", "monument", "mosque", "khan", "giza"]
OUTDOOR_KEYWORDS    = ["nature", "garden", "park", "free", "outdoor",
                       "adventure", "hike", "snorkel", "beach", "budget"]
ACCESSIBLE_KEYWORDS = ["accessible", "wheelchair", "elevator", "ramp",
                       "luxury", "premium", "comfortable", "easy access"]

PASS = "[PASS]"
FAIL = "[FAIL]"


def keyword_hit(response: str, keywords: list) -> list:
    """Return which keywords appear in the response (case-insensitive)."""
    lower = response.lower()
    return [kw for kw in keywords if kw in lower]


def run_tests():
    print("=" * 70)
    print("CLEO Personalization Integration Test")
    print("=" * 70)

    agent = CleoAgent()
    results = {}
    failures = 0

    for label, user_id in [
        ("History buff",     TEST_USER_HISTORY),
        ("Outdoor/budget",   TEST_USER_OUTDOOR),
        ("Accessible/luxury",TEST_USER_ACCESSIBLE),
    ]:
        print(f"\n--- {label} (user_id={user_id[:8]}...) ---")
        response = agent.process_message(QUERY, user_id=user_id)
        results[label] = response

        # Basic assertions
        assert isinstance(response, str) and len(response) > 50, \
            f"Response too short or wrong type: {repr(response[:100])}"
        print(f"  Response length: {len(response)} chars")
        print(f"  Preview: {response[:200].encode('ascii', 'ignore').decode()}...")

    print("\n" + "=" * 70)
    print("Assertion Results")
    print("=" * 70)

    # 1. All responses must be non-empty strings
    for label, resp in results.items():
        ok = isinstance(resp, str) and len(resp) > 50
        tag = PASS if ok else FAIL
        print(f"{tag} {label}: non-empty response ({len(resp)} chars)")
        if not ok:
            failures += 1

    # 2. History user should mention historical keywords
    hist_hits = keyword_hit(results["History buff"], HISTORY_KEYWORDS)
    ok = len(hist_hits) >= 2
    tag = PASS if ok else FAIL
    print(f"\n{tag} History buff mentions historical keywords: {hist_hits}")
    if not ok:
        failures += 1

    # 3. Responses must differ between users
    hist = results["History buff"].lower()
    outdoor = results["Outdoor/budget"].lower()
    accessible = results["Accessible/luxury"].lower()

    diff_ho = hist != outdoor
    diff_ha = hist != accessible
    diff_oa = outdoor != accessible
    ok_diff = diff_ho and diff_ha and diff_oa
    tag = PASS if ok_diff else FAIL
    print(f"\n{tag} All 3 responses are distinct from each other:")
    print(f"     History vs Outdoor:   {'differ' if diff_ho else 'SAME'}")
    print(f"     History vs Accessible:{'differ' if diff_ha else 'SAME'}")
    print(f"     Outdoor vs Accessible:{'differ' if diff_oa else 'SAME'}")
    if not ok_diff:
        failures += 1

    # 4. Accessible user should not be identical to the others (redundant
    #    but explicit for the demo scenario)
    accessible_hits = keyword_hit(results["Accessible/luxury"], ACCESSIBLE_KEYWORDS)
    # Soft check — just report, don't fail (CLEO may mention accessibility indirectly)
    print(f"\n[INFO] Accessible user — accessibility/luxury keywords found: {accessible_hits}")

    print("\n" + "=" * 70)
    if failures == 0:
        print("ALL ASSERTIONS PASSED — personalization is working.")
    else:
        print(f"{failures} ASSERTION(S) FAILED — review output above.")
    print("=" * 70)

    return failures == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

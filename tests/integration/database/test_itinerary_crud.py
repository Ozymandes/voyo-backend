"""
Itinerary CRUD Integration Test

Verifies that itinerary create/read/add-items/list-items operations
work correctly against the live Supabase instance.

Run from project root:
    python tests/integration/database/test_itinerary_crud.py

Requires mock users to be seeded first:
    python scripts/seed_test_users.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.supabase_client import VOYODatabase

# Uses the history buff test user (seeded by seed_test_users.py)
TEST_USER_HISTORY = "11111111-1111-1111-1111-111111111111"

PASS = "[PASS]"
FAIL = "[FAIL]"


def run_tests():
    print("=" * 70)
    print("Itinerary CRUD Integration Test")
    print("=" * 70)

    db = VOYODatabase()
    failures = 0
    itinerary_id = None

    # --- 1. Create itinerary ---
    print("\n[1] create_itinerary")
    itinerary = db.create_itinerary(
        user_id=TEST_USER_HISTORY,
        title="Test Cairo Trip",
        region_id=1
    )
    ok = itinerary is not None and "id" in itinerary
    tag = PASS if ok else FAIL
    print(f"  {tag} Returns dict with 'id': {itinerary}")
    if not ok:
        failures += 1
        print("  Cannot continue without a valid itinerary. Stopping.")
        return False
    itinerary_id = itinerary["id"]

    # --- 2. Retrieve itinerary (by status 'draft') ---
    print("\n[2] get_current_itinerary (status=current — should be None since we created draft)")
    current = db.get_current_itinerary(TEST_USER_HISTORY)
    # We created a 'draft', not 'current', so this should be None or empty
    ok = current is None or current == {}
    tag = PASS if ok else FAIL
    print(f"  {tag} No 'current' itinerary for fresh user: {current}")
    if not ok:
        failures += 1

    # --- 3. Update itinerary status to 'current' ---
    print("\n[3] Update itinerary status to 'current'")
    updated = db.db.update_record(
        "itineraries",
        record_id=itinerary_id,
        data={"status": "current"},
        use_admin=True
    )
    ok = updated is not None
    tag = PASS if ok else FAIL
    print(f"  {tag} Update returned: {updated}")
    if not ok:
        failures += 1

    # --- 4. Retrieve current itinerary ---
    print("\n[4] get_current_itinerary (after status update)")
    current = db.get_current_itinerary(TEST_USER_HISTORY)
    ok = current is not None and current.get("id") == itinerary_id
    tag = PASS if ok else FAIL
    print(f"  {tag} Returns correct itinerary: {current}")
    if not ok:
        failures += 1

    # --- 5. Add POI-linked item (Day 1, seq 1) ---
    print("\n[5] add_itinerary_item — POI-linked item")
    item1 = db.add_itinerary_item(itinerary_id, {
        "poi_id": None,          # No specific POI id needed for test
        "day_number": 1,
        "sequence_order": 1,
        "start_time": "09:00:00",
        "end_time": "12:00:00",
        "custom_title": "Morning at the Pyramids",
        "custom_description": "Visit the Giza Plateau",
        "agent_suggested": True,
        "is_booked": False,
    })
    ok = item1 is not None and "id" in item1
    tag = PASS if ok else FAIL
    print(f"  {tag} Item 1 inserted: id={item1.get('id') if item1 else None}")
    if not ok:
        failures += 1

    # --- 6. Add custom event (Day 1, seq 2) ---
    print("\n[6] add_itinerary_item — custom event")
    item2 = db.add_itinerary_item(itinerary_id, {
        "poi_id": None,
        "day_number": 1,
        "sequence_order": 2,
        "start_time": "14:00:00",
        "end_time": "17:00:00",
        "custom_title": "Egyptian Museum",
        "custom_description": "Explore ancient artifacts",
        "custom_location": "Tahrir Square, Cairo",
        "agent_suggested": True,
        "is_booked": False,
    })
    ok = item2 is not None and "id" in item2
    tag = PASS if ok else FAIL
    print(f"  {tag} Item 2 inserted: id={item2.get('id') if item2 else None}")
    if not ok:
        failures += 1

    # --- 7. List items ordered by day/sequence ---
    print("\n[7] get_itinerary_items — returns 2 items ordered by day/sequence")
    items = db.get_itinerary_items(itinerary_id)
    ok_count = len(items) == 2
    ok_order = (
        ok_count
        and items[0].get("day_number") == 1
        and items[0].get("sequence_order") == 1
        and items[1].get("sequence_order") == 2
    )
    tag = PASS if (ok_count and ok_order) else FAIL
    print(f"  {tag} Count={len(items)}, ordered correctly={ok_order}")
    for item in items:
        print(f"       Day {item.get('day_number')} seq {item.get('sequence_order')}: "
              f"{item.get('custom_title')}")
    if not (ok_count and ok_order):
        failures += 1

    # --- Cleanup: delete test itinerary (cascades to items) ---
    print("\n[cleanup] Deleting test itinerary...")
    deleted = db.db.admin_client.table("itineraries").delete().eq("id", itinerary_id).execute()
    print(f"  Deleted itinerary id={itinerary_id}")

    print("\n" + "=" * 70)
    if failures == 0:
        print("ALL ASSERTIONS PASSED — itinerary CRUD is working.")
    else:
        print(f"{failures} ASSERTION(S) FAILED — review output above.")
    print("=" * 70)

    return failures == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)


import os
import time
import pytest
import json
from history_loader import fetch_btc_history, CACHE_FILE

REFERENCE_FILE = "btc_history_reference.json"

def test_fetch_btc_history():
    # Ensure fresh start
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    data = fetch_btc_history(start_date="2024-01-01")
    assert len(data) > 0
    assert "date" in data[0]
    assert "price" in data[0]
    assert os.path.exists(CACHE_FILE)

def test_history_caching():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    start_time = time.time()
    data1 = fetch_btc_history(start_date="2024-01-01")
    duration1 = time.time() - start_time

    start_time = time.time()
    data2 = fetch_btc_history(start_date="2024-01-01")
    duration2 = time.time() - start_time

    assert len(data1) == len(data2)
    assert duration2 < 0.5

def test_cache_expiry():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    fetch_btc_history(start_date="2024-01-01")

    # Manually expire cache
    old_time = time.time() - 3601
    os.utime(CACHE_FILE, (old_time, old_time))

    start_time = time.time()
    data = fetch_btc_history(start_date="2024-01-01")

    assert len(data) > 0

def test_remote_vs_reference():
    """
    Test that the remote API results match our checked-in reference data for the same period.
    This ensures that the API data format hasn't changed and historical data is consistent.
    """
    if not os.path.exists(REFERENCE_FILE):
        pytest.skip(f"Reference file {REFERENCE_FILE} not found")

    with open(REFERENCE_FILE, "r") as f:
        reference_data = json.load(f)

    # Force a fresh fetch from the remote API
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    start_date = reference_data[0]['date']
    # Fetch from API
    remote_data = fetch_btc_history(start_date=start_date)

    # Create a map for easy comparison
    remote_map = {d['date']: d['price'] for d in remote_data}

    for ref_entry in reference_data:
        date = ref_entry['date']
        ref_price = ref_entry['price']

        assert date in remote_map, f"Date {date} missing from remote data"
        # Use approx for float comparison
        assert remote_map[date] == pytest.approx(ref_price, rel=1e-5), f"Price mismatch for {date}"

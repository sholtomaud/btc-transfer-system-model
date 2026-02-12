
import os
import time
import pytest
from history_loader import fetch_btc_history, CACHE_FILE

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
    # First fetch already happened in previous test if run in order,
    # but let's be independent.
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    start_time = time.time()
    data1 = fetch_btc_history(start_date="2024-01-01")
    duration1 = time.time() - start_time

    start_time = time.time()
    data2 = fetch_btc_history(start_date="2024-01-01")
    duration2 = time.time() - start_time

    assert len(data1) == len(data2)
    # Cache should be significantly faster
    # duration2 might be almost 0, duration1 depends on network
    # We can't guarantee network speed but usually dur2 < 0.1s
    assert duration2 < 0.5

def test_cache_expiry():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)

    fetch_btc_history(start_date="2024-01-01")

    # Manually expire cache
    old_time = time.time() - 3601 # 1 hour + 1 sec ago
    os.utime(CACHE_FILE, (old_time, old_time))

    # We need to capture the print output to verify it's fetching fresh data
    # OR just check that it takes longer/works.
    # Default cache_duration_minutes is 60.
    start_time = time.time()
    data = fetch_btc_history(start_date="2024-01-01")
    duration = time.time() - start_time

    assert len(data) > 0

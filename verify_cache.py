
from history_loader import fetch_btc_history
import os
import time

CACHE_FILE = "btc_history_cache.json"

def test_cache():
    print("Testing Caching Mechanism...")
    
    # Remove cache if exists for clean test
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Removed existing cache file.")
        
    start_time = time.time()
    print("\n--- First Fetch (should be fresh) ---")
    data1 = fetch_btc_history(start_date="2024-01-01", cache_duration_minutes=1)
    duration1 = time.time() - start_time
    print(f"First fetch took {duration1:.2f} seconds. Records: {len(data1)}")
    
    if not os.path.exists(CACHE_FILE):
        print("ERROR: Cache file was not created.")
        return

    start_time = time.time()
    print("\n--- Second Fetch (should be cached) ---")
    data2 = fetch_btc_history(start_date="2024-01-01", cache_duration_minutes=1)
    duration2 = time.time() - start_time
    print(f"Second fetch took {duration2:.2f} seconds. Records: {len(data2)}")
    
    if duration2 < duration1 * 0.1:
        print("SUCCESS: Second fetch was much faster (likely cached).")
    else:
        print("WARNING: Second fetch duration didn't drop significantly.")

    print("\n--- Third Fetch (cache expired) ---")
    # Set cache duration to 0 to force refresh or just wait/mod file mtime
    # Actually our logic uses os.path.getmtime
    # Let's manually set mtime back in time
    old_time = time.time() - 120 # 2 mins ago
    os.utime(CACHE_FILE, (old_time, old_time))
    
    start_time = time.time()
    data3 = fetch_btc_history(start_date="2024-01-01", cache_duration_minutes=1)
    duration3 = time.time() - start_time
    print(f"Third fetch took {duration3:.2f} seconds. Records: {len(data3)}")
    
    if duration3 > duration2:
        print("SUCCESS: Third fetch refreshed after expiration.")
    else:
        print("WARNING: Third fetch was still fast?")

if __name__ == "__main__":
    test_cache()

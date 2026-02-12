
import yfinance as yf
import pandas as pd
from typing import List, Dict
import os
import json
import time

CACHE_FILE = "btc_history_cache.json"

def fetch_btc_history(start_date: str = "2015-01-01", cache_duration_minutes: int = 60) -> List[Dict]:
    """
    Fetches daily BTC-USD history from Yahoo Finance.
    Returns a list of dicts: [{'date': 'YYYY-MM-DD', 'price': float}, ...]
    
    Uses a local JSON cache file to strict updates.
    """
    try:
        # Check cache
        if os.path.exists(CACHE_FILE):
            last_modified = os.path.getmtime(CACHE_FILE)
            if (time.time() - last_modified) < (cache_duration_minutes * 60):
                # Cache is valid
                try:
                    with open(CACHE_FILE, "r") as f:
                        data = json.load(f)
                        # Minimal validation: check if start_date is covered? 
                        # For simplicity, we just return cached data. 
                        # If user changes start_date drastically, they might need to clear cache or we handle it.
                        # Assuming start_date is usually static or similar.
                        if data and data[0]['date'] <= start_date:
                             return [d for d in data if d['date'] >= start_date]
                except Exception as e:
                    print(f"Error reading cache: {e}")

        # Fetch fresh data
        print("Fetching fresh BTC data from Yahoo Finance...")
        btc = yf.Ticker("BTC-USD")
        
        # Fetch history
        # We assume end date is "now"
        df = btc.history(start=start_date, interval="1d")
        
        if df.empty:
            return []
            
        # Format
        history = []
        for index, row in df.iterrows():
            # index is Timestamp
            date_str = index.strftime("%Y-%m-%d")
            price = float(row['Close'])
            history.append({"date": date_str, "price": price})
            
        # Save to cache
        with open(CACHE_FILE, "w") as f:
            json.dump(history, f)
            
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

if __name__ == "__main__":
    data = fetch_btc_history(start_date="2024-01-01")
    print(f"Fetched {len(data)} records.")
    if data:
        print("First:", data[0])
        print("Last:", data[-1])

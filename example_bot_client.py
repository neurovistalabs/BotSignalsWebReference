"""
Example: How to call the signals endpoint from your trading bot
"""
import requests
import json
from typing import List, Dict, Optional

# Configuration
SIGNALS_API_URL = "http://localhost:5000"  # Change to your server URL


def get_latest_signals(limit: int = 10) -> Optional[Dict]:
    """
    Get the latest trading signals from the API
    
    Args:
        limit: Number of recent signals to retrieve (default: 10)
    
    Returns:
        Dictionary with status, count, and signals list, or None on error
    """
    try:
        response = requests.get(
            f"{SIGNALS_API_URL}/signals",
            params={"limit": limit},
            timeout=5
        )
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching signals: {e}")
        return None


def get_latest_signal() -> Optional[Dict]:
    """
    Get only the most recent signal
    
    Returns:
        Single signal dictionary, or None on error
    """
    result = get_latest_signals(limit=1)
    if result and result.get("status") == "success" and result.get("signals"):
        return result["signals"][0]
    return None


def process_signals():
    """
    Example: Continuously poll for new signals and process them
    """
    last_signal_timestamp = None
    
    while True:
        # Get latest signals
        result = get_latest_signals(limit=1)
        
        if result and result.get("status") == "success":
            signals = result.get("signals", [])
            
            if signals:
                latest_signal = signals[0]
                current_timestamp = latest_signal.get("timestamp")
                
                # Process only if it's a new signal
                if current_timestamp != last_signal_timestamp:
                    print(f"New signal received: {latest_signal}")
                    
                    # Process the signal (place order, etc.)
                    process_single_signal(latest_signal)
                    
                    last_signal_timestamp = current_timestamp
        
        # Wait before checking again
        import time
        time.sleep(1)  # Check every second


def process_single_signal(signal: Dict):
    """
    Process a single trading signal
    
    Args:
        signal: Signal dictionary with action, symbol, price, etc.
    """
    action = signal.get("action")  # BUY or SELL
    symbol = signal.get("symbol")  # e.g., BTCUSDT
    price = signal.get("price")
    quantity = signal.get("quantity")
    strategy = signal.get("strategy")
    
    print(f"\n📊 Processing Signal:")
    print(f"   Action: {action}")
    print(f"   Symbol: {symbol}")
    print(f"   Price: {price}")
    print(f"   Quantity: {quantity}")
    print(f"   Strategy: {strategy}")
    
    # TODO: Add your trading logic here
    # Example:
    # if action == "BUY":
    #     place_buy_order(symbol, quantity, price)
    # elif action == "SELL":
    #     place_sell_order(symbol, quantity, price)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Trading Bot - Signals API Client Example")
    print("=" * 60)
    
    # Example 1: Get the 5 most recent signals
    print("\n1. Getting 5 most recent signals...")
    result = get_latest_signals(limit=5)
    if result:
        print(f"   Status: {result['status']}")
        print(f"   Count: {result['count']}")
        print(f"   Signals:")
        for i, signal in enumerate(result['signals'], 1):
            print(f"      {i}. {signal.get('action')} {signal.get('symbol')} @ {signal.get('price')}")
    
    # Example 2: Get only the latest signal
    print("\n2. Getting latest signal...")
    latest = get_latest_signal()
    if latest:
        print(f"   Latest: {json.dumps(latest, indent=2)}")
    
    # Example 3: Process signals (uncomment to run continuously)
    # print("\n3. Starting signal monitoring...")
    # process_signals()






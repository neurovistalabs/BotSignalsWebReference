"""
Test script to send sample trading signals to the webhook endpoint.
This populates the in-memory storage with test data.

Usage:
    python test_send_signals.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"  # Change to your server URL

# Sample trading signals to send
SAMPLE_SIGNALS = [
    # {
    #     "action": "BUY",
    #     "symbol": "BTCUSDT",
    #     "price": 45000.50,
    #     "quantity": 0.1,
    #     "strategy": "MomentumStrategy"
    # },
    {
        "action": "SELL",
        "symbol": "ETHUSDT",
        "price": 2800.75,
        "quantity": 1.5,
        "strategy": "RSIStrategy"
    }
    # {
    #     "action": "BUY",
    #     "symbol": "BNBUSDT",
    #     "price": 320.25,
    #     "quantity": 5.0,
    #     "strategy": "BreakoutStrategy"
    # },
    # {
    #     "action": "BUY",
    #     "symbol": "ADAUSDT",
    #     "price": 0.55,
    #     "quantity": 1000.0,
    #     "strategy": "TrendFollowing"
    # },
    # {
    #     "action": "SELL",
    #     "symbol": "SOLUSDT",
    #     "price": 95.80,
    #     "quantity": 10.0,
    #     "strategy": "MeanReversion"
    # },
    # {
    #     "action": "BUY",
    #     "symbol": "BTCUSDT",
    #     "price": 45100.00,
    #     "quantity": 0.05,
    #     "strategy": "ScalpingStrategy"
    # },
    # {
    #     "action": "SELL",
    #     "symbol": "ETHUSDT",
    #     "price": 2815.50,
    #     "quantity": 2.0,
    #     "strategy": "MomentumStrategy"
    # },
    # {
    #     "action": "BUY",
    #     "symbol": "XRPUSDT",
    #     "price": 0.62,
    #     "quantity": 500.0,
    #     "strategy": "BreakoutStrategy"
    # },
    # {
    #     "action": "BUY",
    #     "symbol": "DOGEUSDT",
    #     "price": 0.085,
    #     "quantity": 10000.0,
    #     "strategy": "TrendFollowing"
    # },
    # {
    #     "action": "SELL",
    #     "symbol": "BTCUSDT",
    #     "price": 45200.25,
    #     "quantity": 0.08,
    #     "strategy": "ProfitTaking"
    # }
]


def send_signal(signal_data):
    """
    Send a single signal to the webhook endpoint
    
    Args:
        signal_data: Dictionary containing signal data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=signal_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "success":
            print(f"✅ Sent: {signal_data['action']} {signal_data['symbol']} @ {signal_data['price']}")
            return True
        else:
            print(f"❌ Failed: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {WEBHOOK_URL}")
        print("   Make sure the Flask app is running!")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def send_all_signals(signals, delay=0.5):
    """
    Send multiple signals to the webhook
    
    Args:
        signals: List of signal dictionaries
        delay: Delay in seconds between signals (default: 0.5)
    """
    print("=" * 60)
    print("Sending Test Signals to Webhook")
    print("=" * 60)
    print(f"Webhook URL: {WEBHOOK_URL}\n")
    
    success_count = 0
    failed_count = 0
    
    for i, signal in enumerate(signals, 1):
        print(f"[{i}/{len(signals)}] ", end="")
        if send_signal(signal):
            success_count += 1
        else:
            failed_count += 1
        
        # Add delay between requests (except for the last one)
        if i < len(signals) and delay > 0:
            time.sleep(delay)
    
    print("\n" + "=" * 60)
    print(f"Summary: {success_count} successful, {failed_count} failed")
    print("=" * 60)
    
    if success_count > 0:
        print(f"\n✅ {success_count} signals stored in memory!")
        print("   You can now test the /signals endpoint:")
        print(f"   curl http://localhost:5000/signals?limit={success_count}")


def send_single_signal(action, symbol, price, quantity, strategy="TestStrategy"):
    """
    Convenience function to send a single custom signal
    
    Args:
        action: "BUY" or "SELL"
        symbol: Trading pair (e.g., "BTCUSDT")
        price: Price value
        quantity: Quantity value
        strategy: Strategy name (optional)
    """
    signal = {
        "action": action,
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "strategy": strategy
    }
    return send_signal(signal)


if __name__ == "__main__":
    import sys
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        WEBHOOK_URL = sys.argv[1]
        print(f"Using custom URL: {WEBHOOK_URL}\n")
    
    # Send all sample signals
    send_all_signals(SAMPLE_SIGNALS, delay=0.3)
    
    # Example: Send a custom signal
    # print("\n" + "=" * 60)
    # print("Sending Custom Signal")
    # print("=" * 60)
    # send_single_signal("BUY", "MATICUSDT", 0.85, 100.0, "CustomTest")


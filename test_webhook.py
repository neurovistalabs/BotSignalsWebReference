"""
Simple test script to test the webhook endpoints
Run this after starting the Flask app (python app.py)
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_webhook():
    """Test sending a signal to the webhook endpoint"""
    print("Testing webhook endpoint...")
    
    # Sample signal data
    signal = {
        "action": "BUY",
        "symbol": "BTCUSDT",
        "price": 45000,
        "quantity": 0.1,
        "strategy": "test_strategy"
    }
    
    response = requests.post(
        f"{BASE_URL}/webhook",
        json=signal,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_signals(limit=5):
    """Test retrieving signals"""
    print(f"\nTesting signals endpoint (limit={limit})...")
    
    response = requests.get(f"{BASE_URL}/signals?limit={limit}")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_health():
    """Test health check endpoint"""
    print("\nTesting health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Crypto Trading Bot Signals Web Service")
    print("=" * 50)
    
    # Test health check first
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        exit(1)
    
    # Test webhook
    if test_webhook():
        print("\n✅ Webhook test passed!")
    else:
        print("\n❌ Webhook test failed!")
    
    # Wait a moment
    time.sleep(0.5)
    
    # Test getting signals
    if test_get_signals(5):
        print("\n✅ Get signals test passed!")
    else:
        print("\n❌ Get signals test failed!")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("=" * 50)


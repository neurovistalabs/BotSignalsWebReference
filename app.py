from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import redis
from redis.exceptions import RedisError, ConnectionError

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Redis key for signals list
REDIS_SIGNALS_KEY = 'signals:list'
MAX_SIGNALS = 1000

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,  # Automatically decode responses to strings
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
except (ConnectionError, RedisError) as e:
    print(f"Warning: Could not connect to Redis: {e}")
    print("Please ensure Redis is running and accessible.")
    redis_client = None

def load_signals():
    """Load signals from Redis"""
    if redis_client is None:
        return []
    
    try:
        # Get all signals from Redis list (they're stored as JSON strings)
        signals_json = redis_client.lrange(REDIS_SIGNALS_KEY, 0, MAX_SIGNALS - 1)
        
        # Parse each JSON string back to dictionary
        signals = []
        for signal_json in signals_json:
            try:
                signals.append(json.loads(signal_json))
            except json.JSONDecodeError:
                # Skip corrupted entries
                continue
        
        return signals
    except (RedisError, ConnectionError) as e:
        print(f"Error loading signals from Redis: {e}")
        return []

def save_signal(signal_data):
    """Save a single signal to Redis"""
    if redis_client is None:
        raise RedisError("Redis connection not available")
    
    try:
        # Convert signal to JSON string
        signal_json = json.dumps(signal_data)
        
        # Add signal to the beginning of the list
        redis_client.lpush(REDIS_SIGNALS_KEY, signal_json)
        
        # Trim list to keep only the last MAX_SIGNALS
        redis_client.ltrim(REDIS_SIGNALS_KEY, 0, MAX_SIGNALS - 1)
        
    except (RedisError, ConnectionError) as e:
        print(f"Error saving signal to Redis: {e}")
        raise

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive signal from TradingView webhook"""
    try:
        # Get the signal data from the request
        signal_data = request.get_json()
        
        if not signal_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Add timestamp to the signal
        signal_data['timestamp'] = datetime.now().isoformat()
        signal_data['received_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save signal to Redis
        save_signal(signal_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Signal received and stored',
            'timestamp': signal_data['timestamp']
        }), 200
        
    except (RedisError, ConnectionError) as e:
        return jsonify({
            'error': 'Redis storage error',
            'message': str(e)
        }), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signals', methods=['GET'])
def get_signals():
    """Get recent signals for the trading bot"""
    try:
        # Get optional query parameters
        limit = request.args.get('limit', default=10, type=int)
        
        # Load signals
        signals = load_signals()
        
        # Return the most recent signals (they're already sorted by most recent first)
        recent_signals = signals[:limit]
        
        return jsonify({
            'status': 'success',
            'count': len(recent_signals),
            'signals': recent_signals
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check Redis connection
        if redis_client is None:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Redis connection not available'
            }), 503
        
        # Test Redis connection
        redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'redis': 'connected'
        }), 200
    except (RedisError, ConnectionError) as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'Redis connection error: {str(e)}'
        }), 503

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, request, jsonify
from datetime import datetime
import threading

app = Flask(__name__)

# In-memory storage for signals
MAX_SIGNALS = 1000
_signals = []  # List to store signals (most recent first)
_signals_lock = threading.Lock()  # Thread lock for thread-safe operations

def load_signals():
    """Load signals from in-memory storage"""
    with _signals_lock:
        # Return a copy to avoid external modification
        return _signals.copy()

def pop_signals(count):
    """Remove and return the most recent signals from in-memory storage (queue behavior)"""
    with _signals_lock:
        if not _signals:
            return []
        
        # Get the most recent signals (first N in the list)
        signals_to_return = _signals[:count]
        
        # Remove them from memory
        _signals[:] = _signals[count:]
        
        return signals_to_return

def save_signal(signal_data):
    """Save a single signal to in-memory storage"""
    with _signals_lock:
        # Add signal to the beginning of the list (most recent first)
        _signals.insert(0, signal_data)
        
        # Trim list to keep only the last MAX_SIGNALS
        if len(_signals) > MAX_SIGNALS:
            _signals[:] = _signals[:MAX_SIGNALS]

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
        
        # Save signal to in-memory storage
        save_signal(signal_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Signal received and stored',
            'timestamp': signal_data['timestamp']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signals', methods=['GET'])
def get_signals():
    """Get recent signals for the trading bot and remove them from memory"""
    try:
        # Get optional query parameters
        limit = request.args.get('limit', default=10, type=int)
        
        # Pop signals from memory (removes them after retrieving)
        recent_signals = pop_signals(limit)
        
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
        signal_count = len(_signals)
        return jsonify({
            'status': 'healthy',
            'storage': 'in-memory',
            'signals_count': signal_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': str(e)
        }), 503

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


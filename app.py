from flask import Flask, request, jsonify
from datetime import datetime
import threading
import json
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Receive signal from TradingView webhook - optimized for fast response"""
    try:
        # Optimized parsing: try JSON first, then fallback to text
        signal_data = None
        
        # Fast path: try to get JSON directly
        if request.is_json:
            signal_data = request.get_json(silent=True, force=False)
        
        # If no JSON, try parsing raw data
        if not signal_data:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                try:
                    signal_data = json.loads(raw_data)
                except (json.JSONDecodeError, ValueError):
                    # Treat as plain text
                    signal_data = {'message': raw_data, 'raw': True}
        
        if not signal_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Ensure signal_data is a dict
        if not isinstance(signal_data, dict):
            signal_data = {'data': signal_data}
        
        # Add timestamp (single datetime.now() call for efficiency)
        now = datetime.now()
        signal_data['timestamp'] = now.isoformat()
        signal_data['received_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save signal to in-memory storage
        try:
            save_signal(signal_data)
        except Exception as save_err:
            logger.error(f"Error saving signal: {save_err}", exc_info=True)
            return jsonify({
                'status': 'warning',
                'message': 'Signal received but storage failed',
                'error': str(save_err)
            }), 200
        
        # Return quickly (TradingView requires response within 3 seconds)
        return jsonify({
            'status': 'success',
            'message': 'Signal received and stored',
            'timestamp': signal_data['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        try:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        except Exception:
            return '{"error":"Internal server error"}', 500, {'Content-Type': 'application/json'}

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
    # Run the Flask app (for local development only)
    # In production, Render uses gunicorn (see Procfile)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    logger.info(f"Starting Flask app on port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Log when running under gunicorn
    logger.info("Flask app initialized (running under gunicorn)")


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
    """Receive signal from TradingView webhook"""
    try:
        # TradingView sends JSON if the alert message is valid JSON,
        # otherwise it sends text/plain. Handle both cases.
        signal_data = None
        
        # Log incoming request details for debugging
        content_type = request.content_type
        logger.info(f"Webhook received: Content-Type={content_type}, is_json={request.is_json}")
        
        # Try to get JSON data first
        if request.is_json:
            signal_data = request.get_json()
            logger.debug(f"Parsed JSON data: {signal_data}")
        else:
            # If not JSON, try to parse the raw text as JSON
            try:
                raw_data = request.get_data(as_text=True)
                logger.debug(f"Raw data received: {raw_data[:200]}")  # Log first 200 chars
                if raw_data:
                    signal_data = json.loads(raw_data)
                    logger.debug(f"Parsed raw data as JSON: {signal_data}")
            except (json.JSONDecodeError, ValueError):
                # If it's not JSON, treat it as plain text and create a signal object
                raw_data = request.get_data(as_text=True)
                logger.info(f"Received plain text (not JSON): {raw_data[:200]}")
                if raw_data:
                    signal_data = {
                        'message': raw_data,
                        'raw': True
                    }
        
        if not signal_data:
            logger.warning("Webhook received request with no data")
            return jsonify({'error': 'No data received'}), 400
        
        # Add timestamp to the signal
        signal_data['timestamp'] = datetime.now().isoformat()
        signal_data['received_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save signal to in-memory storage
        save_signal(signal_data)
        
        # Log signal details - show what keys are present and key values
        action = signal_data.get('action', signal_data.get('Action', 'N/A'))
        symbol = signal_data.get('symbol', signal_data.get('Symbol', signal_data.get('ticker', 'N/A')))
        signal_keys = list(signal_data.keys())
        logger.info(f"Signal received and stored: action={action}, symbol={symbol}, keys={signal_keys}")
        
        # Return quickly (TradingView requires response within 3 seconds)
        return jsonify({
            'status': 'success',
            'message': 'Signal received and stored',
            'timestamp': signal_data['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
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
    # Run the Flask app (for local development only)
    # In production, Render uses gunicorn (see Procfile)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)


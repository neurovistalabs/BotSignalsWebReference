from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# File to store signals
SIGNALS_FILE = 'signals.json'

def load_signals():
    """Load signals from file"""
    if not os.path.exists(SIGNALS_FILE):
        return []
    try:
        with open(SIGNALS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_signals(signals):
    """Save signals to file"""
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(signals, f, indent=2)

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
        
        # Load existing signals
        signals = load_signals()
        
        # Add new signal at the beginning (most recent first)
        signals.insert(0, signal_data)
        
        # Keep only the last 1000 signals (optional, to prevent file from growing too large)
        signals = signals[:1000]
        
        # Save signals
        save_signals(signals)
        
        return jsonify({
            'status': 'success',
            'message': 'Signal received and stored',
            'timestamp': signal_data['timestamp']
        }), 200
        
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
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


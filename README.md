# Crypto Trading Bot Signals Web Service

A simple Python web service that receives trading signals from TradingView webhooks and provides an API for your trading bot to retrieve recent signals.

## Features

- **Webhook Endpoint**: Receives POST requests from TradingView and stores signals in a JSON file
- **Signals Endpoint**: Returns recent signals for your trading bot
- **Simple Storage**: Signals are stored in a JSON file (easy to inspect and debug)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```bash
   python app.py
   ```

   The service will start on `http://localhost:5000`

## API Endpoints

### 1. POST /webhook
Receives signals from TradingView webhooks.

**Request**: POST request with JSON body containing the signal data

**Example**:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "BUY",
    "symbol": "BTCUSDT",
    "price": 45000,
    "quantity": 0.1
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "Signal received and stored",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 2. GET /signals
Returns recent signals for your trading bot.

**Query Parameters**:
- `limit` (optional): Number of recent signals to return (default: 10)

**Example**:
```bash
curl http://localhost:5000/signals?limit=5
```

**Response**:
```json
{
  "status": "success",
  "count": 5,
  "signals": [
    {
      "action": "BUY",
      "symbol": "BTCUSDT",
      "price": 45000,
      "quantity": 0.1,
      "timestamp": "2024-01-15T10:30:00.123456",
      "received_at": "2024-01-15 10:30:00"
    },
    ...
  ]
}
```

### 3. GET /health
Health check endpoint.

**Example**:
```bash
curl http://localhost:5000/health
```

## TradingView Webhook Setup

In your TradingView alert, use the following webhook URL:
```
http://your-server-ip:5000/webhook
```

**TradingView Alert Message Example** (JSON format):
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "quantity": 0.1,
  "strategy": "{{strategy.name}}"
}
```

## Testing

### Test the webhook endpoint:
```bash
# Test with a sample signal
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "BUY",
    "symbol": "BTCUSDT",
    "price": 45000,
    "quantity": 0.1
  }'
```

### Test the signals endpoint:
```bash
# Get the 5 most recent signals
curl http://localhost:5000/signals?limit=5
```

## Storage

Signals are stored in `signals.json` in the same directory as the application. The file format is a JSON array with the most recent signals first.

## Notes

- The service keeps the last 1000 signals to prevent the file from growing too large
- Each signal is automatically timestamped when received
- The service runs in debug mode by default (change `debug=True` to `debug=False` in production)


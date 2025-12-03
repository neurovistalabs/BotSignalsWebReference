# Crypto Trading Bot Signals Web Service

A simple Python web service that receives trading signals from TradingView webhooks and provides an API for your trading bot to retrieve recent signals.

## Features

- **Webhook Endpoint**: Receives POST requests from TradingView and stores signals in Redis
- **Signals Endpoint**: Returns recent signals for your trading bot
- **Redis Storage**: Fast, scalable signal storage using Redis
- **Health Monitoring**: Health check endpoint includes Redis connection status

## Setup

1. **Install Redis**:
   
   **Option A: Using Docker (Recommended for development)**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```
   
   **Option B: Native Installation**
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Linux: `sudo apt-get install redis-server` or `sudo yum install redis`
   - macOS: `brew install redis`
   - Then start Redis: `redis-server`

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Redis (Optional)**:
   
   The service uses the following environment variables (defaults shown):
   ```bash
   REDIS_HOST=localhost      # Redis server host
   REDIS_PORT=6379           # Redis server port
   REDIS_DB=0                # Redis database number
   REDIS_PASSWORD=           # Redis password (optional, leave empty if no password)
   ```
   
   Example with custom configuration:
   ```bash
   export REDIS_HOST=localhost
   export REDIS_PORT=6379
   export REDIS_PASSWORD=your_password
   python app.py
   ```

4. **Run the service**:
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

Signals are stored in Redis using a list data structure. The Redis key used is `signals:list`. Signals are stored as JSON strings in the list, with the most recent signals first.

### Benefits of Redis Storage

- **Performance**: Much faster than file I/O, especially under concurrent load
- **Scalability**: Multiple application instances can share the same Redis instance
- **Concurrency**: Better handling of concurrent webhook requests
- **Persistence**: Redis can be configured for persistence (RDB/AOF snapshots)
- **Flexibility**: Easy to add features like signal expiration, counters, and time-based queries

### Redis Configuration

The service automatically connects to Redis on startup. If Redis is not available, the service will start but will return errors when trying to store or retrieve signals. Check the `/health` endpoint to verify Redis connectivity.

### Migration from JSON File

If you previously used the JSON file storage, you can either:
- Start fresh with Redis (old `signals.json` file will be ignored)
- Use the migration script to import existing signals:
  ```bash
  python migrate_json_to_redis.py
  ```

## Notes

- The service keeps the last 1000 signals to prevent excessive memory usage
- Each signal is automatically timestamped when received
- The service runs in debug mode by default (change `debug=True` to `debug=False` in production)
- Redis must be running and accessible for the service to function properly
- Check the `/health` endpoint to verify Redis connection status


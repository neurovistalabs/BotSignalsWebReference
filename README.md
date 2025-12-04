# Crypto Trading Bot Signals Web Service

A simple Python web service that receives trading signals from TradingView webhooks and provides an API for your trading bot to retrieve recent signals.

## Features

- **Webhook Endpoint**: Receives POST requests from TradingView and stores signals in memory
- **Signals Endpoint**: Returns recent signals for your trading bot
- **In-Memory Storage**: Fast, thread-safe signal storage - no external dependencies required
- **Health Monitoring**: Health check endpoint shows storage status and signal count
- **Deployment Ready**: Works on Render, Heroku, and other platforms without additional services

## Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```bash
   python app.py
   ```

   The service will start on `http://localhost:5000`

## Deployment

### Deploying to Render (or similar platforms)

When deploying to Render or similar platforms:

1. **HTTPS is automatically handled** - Render provides HTTPS on port 443, which TradingView requires
2. **Use the `/webhook` endpoint** - Your webhook URL will be: `https://your-app.onrender.com/webhook`
3. **Update your C# client** - Change the API URL to your deployed URL:
   ```csharp
   var client = new SignalsApiClient("https://your-app.onrender.com");
   ```

### Important for TradingView:
- ✅ Your deployed service will automatically use HTTPS (port 443)
- ✅ Response time is fast (in-memory storage)
- ✅ Handles both JSON and plain text webhook messages
- ⚠️ Make sure 2FA is enabled on your TradingView account

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

### Important TradingView Requirements:
- **Ports**: Only ports **80** (HTTP) and **443** (HTTPS) are accepted by TradingView
- **Response Time**: Your server must respond within **3 seconds** or the request will be canceled
- **2FA Required**: Webhook alerts require 2-factor authentication on your TradingView account
- **IPv6**: Not currently supported - use IPv4 addresses
- **Content Types**: TradingView sends `application/json` if the message is valid JSON, otherwise `text/plain`

### Webhook URL Configuration:

**For Production (HTTPS on port 443):**
```
https://your-domain.com/webhook
```

**For Development/Testing:**
- Use a service like ngrok to expose your local server:
  ```bash
  ngrok http 5000
  # Then use: https://your-ngrok-url.ngrok.io/webhook
  ```

### TradingView Alert Message Format:

**Recommended JSON Format** (TradingView will send as `application/json`):
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "quantity": 0.1,
  "strategy": "{{strategy.name}}"
}
```

**Alternative**: You can also send plain text, and the service will store it as a message:
```
BUY {{ticker}} at {{close}}
```

### TradingView IP Allowlist (Optional):

If your server has firewall restrictions, allowlist these TradingView IP addresses:
- `52.89.214.238`
- `34.212.75.30`
- `54.218.53.128`
- `52.32.178.7`

## C# Client Example

To get signals from your C# trading bot, use the provided `TradingBotClient.cs` file or the simpler `TradingBotClient_Simple.cs`.

### Quick Example:
```csharp
using System.Net.Http;
using System.Text.Json;

var client = new HttpClient();
string apiUrl = "http://localhost:5000/signals?limit=10";
var response = await client.GetAsync(apiUrl);
var json = await response.Content.ReadAsStringAsync();
// Parse and process signals...
```

### Full Example:
See `TradingBotClient.cs` for a complete implementation with:
- Signal model classes
- Async/await pattern
- Error handling
- Continuous polling example

**Important**: When you retrieve signals via `GET /signals`, they are **removed from memory** (queue behavior). Each signal is consumed once.

## Testing

### Send Test Signals (Recommended):
Use the provided test script to populate the service with sample signals:
```bash
python test_send_signals.py
```

This will send 10 sample trading signals to the webhook endpoint, which you can then retrieve using the `/signals` endpoint.

### Test the webhook endpoint manually:
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
# Get the 5 most recent signals (they will be removed from memory)
curl http://localhost:5000/signals?limit=5
```

**Note**: After retrieving signals, they are removed from memory. Run `test_send_signals.py` again to repopulate if needed.

## Storage

Signals are stored in-memory using a thread-safe Python list. The most recent signals are kept at the beginning of the list, and the service automatically maintains a maximum of 1000 signals to prevent excessive memory usage.

### Benefits of In-Memory Storage

- **No External Dependencies**: No need to install or configure Redis, SQLite, or any other service
- **Simple Deployment**: Works on Render, Heroku, and other platforms without additional services
- **Fast Performance**: In-memory operations are extremely fast
- **Thread-Safe**: Uses Python's threading locks to handle concurrent webhook requests safely
- **Zero Configuration**: Works out of the box with no setup required

### Important Notes

- **Data Persistence**: Signals are stored in memory and will be lost when the application restarts. This is suitable for real-time trading signals where historical data persistence may not be critical.
- **Single Instance**: This storage method works best with a single application instance. For multiple instances, consider using Redis or a database.
- **Memory Usage**: The service automatically limits storage to 1000 signals to prevent excessive memory usage.

## Notes

- The service keeps the last 1000 signals to prevent excessive memory usage
- Each signal is automatically timestamped when received
- The service runs in debug mode by default (change `debug=True` to `debug=False` in production)
- Signals are stored in memory and will be lost when the application restarts
- The storage is thread-safe and handles concurrent webhook requests safely
- Check the `/health` endpoint to verify service status and signal count


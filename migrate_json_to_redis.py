"""
Optional migration script to import existing signals.json into Redis.
Run this once if you want to migrate existing signals from JSON file to Redis.

Usage:
    python migrate_json_to_redis.py
"""
import json
import os
import redis
from redis.exceptions import RedisError, ConnectionError

# Redis configuration (same as app.py)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

REDIS_SIGNALS_KEY = 'signals:list'
SIGNALS_FILE = 'signals.json'

def migrate_signals():
    """Migrate signals from JSON file to Redis"""
    
    # Check if JSON file exists
    if not os.path.exists(SIGNALS_FILE):
        print(f"❌ {SIGNALS_FILE} not found. Nothing to migrate.")
        return False
    
    # Load signals from JSON file
    try:
        with open(SIGNALS_FILE, 'r') as f:
            signals = json.load(f)
        print(f"✅ Loaded {len(signals)} signals from {SIGNALS_FILE}")
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Error reading {SIGNALS_FILE}: {e}")
        return False
    
    if not signals:
        print("ℹ️  No signals to migrate.")
        return True
    
    # Connect to Redis
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        redis_client.ping()
        print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except (ConnectionError, RedisError) as e:
        print(f"❌ Could not connect to Redis: {e}")
        print("Please ensure Redis is running and accessible.")
        return False
    
    # Check if Redis already has signals
    existing_count = redis_client.llen(REDIS_SIGNALS_KEY)
    if existing_count > 0:
        response = input(f"⚠️  Redis already contains {existing_count} signals. "
                        f"Continue migration? This will add {len(signals)} more signals. (y/n): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return False
    
    # Migrate signals to Redis
    # JSON file has most recent first, LPUSH maintains this order
    migrated = 0
    try:
        # Clear existing signals if any
        redis_client.delete(REDIS_SIGNALS_KEY)
        
        # Convert all signals to JSON strings
        # Note: LPUSH with multiple values pushes them in reverse order
        # Since JSON has newest first, we reverse to maintain correct order
        signal_strings = [json.dumps(signal) for signal in reversed(signals)]
        
        # Push all signals at once (LPUSH adds to left/beginning)
        if signal_strings:
            redis_client.lpush(REDIS_SIGNALS_KEY, *signal_strings)
            migrated = len(signal_strings)
            
            # Trim to keep only migrated signals (or max 1000 if more)
            max_signals = min(len(signals), 1000)
            redis_client.ltrim(REDIS_SIGNALS_KEY, 0, max_signals - 1)
        
        print(f"✅ Successfully migrated {migrated} signals to Redis!")
        print(f"   Redis key: {REDIS_SIGNALS_KEY}")
        
        # Verify migration
        final_count = redis_client.llen(REDIS_SIGNALS_KEY)
        print(f"   Total signals in Redis: {final_count}")
        
        return True
        
    except (RedisError, ConnectionError) as e:
        print(f"❌ Error migrating signals to Redis: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Signals Migration: JSON File → Redis")
    print("=" * 60)
    print()
    
    if migrate_signals():
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print("Note: The original signals.json file has not been deleted.")
        print("You can safely delete it after verifying the migration.")
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)


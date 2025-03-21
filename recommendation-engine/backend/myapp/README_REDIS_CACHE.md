# Redis Caching for Source-Destination Routes

This document explains the Redis caching implementation for the Sustainable Travel Recommendation Engine, specifically for caching results that match source and destination airport pairs.

## Overview

The caching system uses Redis to store and retrieve query results for specific source-destination pairs. This significantly improves performance by:

1. Reducing database queries
2. Minimizing API calls
3. Decreasing response time for frequently requested routes

## Setup

### 1. Install Redis

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
```

#### On Windows:
Download and install Redis from [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)

### 2. Environment Variables

Add the following environment variables to your `.env` file:

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password_if_any
REDIS_DB=0
CACHE_EXPIRY=86400  # Cache expiry time in seconds (default: 24 hours)
```

## Usage

### API Endpoints

#### 1. Query with Cache Control

**Endpoint:** `POST /api/query/`

**Request Body:**
```json
{
  "source": "JFK",
  "dest": "LAX",
  "force_refresh": false  // Optional, set to true to bypass cache
}
```

**Response:**
```json
{
  // Query results
}
```

#### 2. Clear Cache

**Endpoint:** `POST /api/cache/clear/`

**Request Body:**
```json
{
  "source": "JFK",  // Optional
  "dest": "LAX"     // Optional
}
```

**Response:**
```json
{
  "message": "Successfully cleared X cache entries"
}
```

**Cache Clearing Options:**
- Provide both `source` and `dest` to clear a specific route
- Provide only `source` to clear all routes from that source
- Provide only `dest` to clear all routes to that destination
- Provide neither to clear all route caches

## Implementation Details

### Cache Keys

Cache keys follow this format:
```
route:{SOURCE}:{DESTINATION}
```

For example, a route from JFK to LAX would have the key:
```
route:JFK:LAX
```

### Cache Decorator

The `@cache_route_results` decorator is used to automatically cache function results based on source and destination parameters:

```python
@cache_route_results
def process_query(source: str, dest: str) -> dict:
    # Function implementation
    return result
```

### Direct Cache Access

You can also directly access the cache using these functions:

```python
from .cache import get_cache, set_cache, delete_cache, get_route_cache_key

# Generate a cache key
key = get_route_cache_key("JFK", "LAX")

# Get cached data
data = get_cache(key)

# Store data in cache (expires in 24 hours by default)
set_cache(key, data, expiry=86400)

# Delete cached data
delete_cache(key)
```

## Monitoring

### Redis CLI

You can monitor Redis using the Redis CLI:

```bash
redis-cli

# List all route keys
KEYS route:*

# Get information about a key
TTL route:JFK:LAX
GET route:JFK:LAX

# Monitor Redis commands in real-time
MONITOR
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to Redis:

1. Verify Redis is running: `redis-cli ping` should return `PONG`
2. Check your connection settings in the environment variables
3. Ensure Redis is listening on the expected port: `netstat -an | grep 6379`

### Cache Not Working

If caching doesn't seem to be working:

1. Check Redis connection by running a simple command: `redis-cli ping`
2. Verify the cache keys exist: `redis-cli keys route:*`
3. Check if the TTL is set correctly: `redis-cli ttl route:JFK:LAX`
4. Ensure the `force_refresh` parameter is not always set to `true` 
import json
import redis
import os
from functools import wraps
from datetime import timedelta

# Initialize Redis client
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
CACHE_EXPIRY = int(os.environ.get('CACHE_EXPIRY', 86400))  # Default: 24 hours
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

redis_client = redis.Redis.from_url(
    REDIS_URL
)
#to run locally
# redis_client = redis.Redis(host='localhost', port=6379)

def get_route_cache_key(source, dest):
    """
    Generate a cache key for a specific route (source to destination)
    
    Args:
        source (str): Source airport code
        dest (str): Destination airport code
        
    Returns:
        str: Cache key
    """
    return f"route:{source.upper()}:{dest.upper()}"

def get_cache(key):
    """
    Get data from Redis cache
    
    Args:
        key (str): Cache key
        
    Returns:
        dict or None: Cached data or None if not found
    """
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None

def set_cache(key, data, expiry=CACHE_EXPIRY):
    """
    Store data in Redis cache
    
    Args:
        key (str): Cache key
        data (dict): Data to cache
        expiry (int): Cache expiry time in seconds (default: 24 hours)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client.setex(
            key,
            expiry,
            json.dumps(data)
        )
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False

def delete_cache(key):
    """
    Delete data from Redis cache
    
    Args:
        key (str): Cache key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis delete error: {e}")
        return False

def cache_route_results(func):
    """
    Decorator for caching route query results
    
    Args:
        func: Function to decorate
        
    Returns:
        function: Decorated function
    """
    @wraps(func)
    def wrapper(source, dest, *args, **kwargs):
        # Check if force_refresh is in kwargs and remove it
        force_refresh = kwargs.pop('force_refresh', False)
        
        # Generate cache key
        cache_key = get_route_cache_key(source, dest)
        
        # If not forcing refresh, try to get from cache
        if not force_refresh:
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                return cached_result
        
        # If not in cache or forcing refresh, call the function
        result = func(source, dest, *args, **kwargs)
        print("Result from cache",result)
        # Cache the result
        set_cache(cache_key, result)
        
        return result
    return wrapper

def clear_route_cache(source=None, dest=None):
    """
    Clear cached data for routes
    
    Args:
        source (str, optional): Source airport code
        dest (str, optional): Destination airport code
        
    Returns:
        int: Number of keys deleted
    """
    try:
        if source and dest:
            # Clear specific route
            key = get_route_cache_key(source, dest)
            return redis_client.delete(key)
        elif source:
            # Clear all routes from a source
            pattern = f"route:{source.upper()}:*"
            keys = redis_client.keys(pattern)
        elif dest:
            # Clear all routes to a destination
            pattern = f"route:*:{dest.upper()}"
            keys = redis_client.keys(pattern)
        else:
            # Clear all routes
            pattern = "route:*"
            keys = redis_client.keys(pattern)
            
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"Redis pattern delete error: {e}")
        return 0 
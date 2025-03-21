"""
Example usage of the Redis caching mechanism for source-destination routes.
This file is for demonstration purposes only.
"""

from .cache import (
    get_cache, 
    set_cache, 
    delete_cache, 
    get_route_cache_key, 
    clear_route_cache,
    cache_route_results
)
from .langchain import process_query

def example_direct_cache_usage():
    """Example of directly using the cache functions."""
    # Generate a cache key for JFK to LAX
    cache_key = get_route_cache_key("JFK", "LAX")
    
    # Check if we have cached data
    cached_data = get_cache(cache_key)
    
    if cached_data:
        print("Found cached data:", cached_data)
    else:
        print("No cached data found, fetching fresh data...")
        
        # Fetch fresh data (this is just an example)
        fresh_data = {
            "flights": [
                {"airline": "Delta", "carbon_emission": 120},
                {"airline": "United", "carbon_emission": 150}
            ]
        }
        
        # Cache the fresh data (expires in 24 hours by default)
        set_cache(cache_key, fresh_data)
        print("Data cached successfully")
        
        # Return the fresh data
        return fresh_data
    
    # Return the cached data
    return cached_data

def example_decorator_usage():
    """Example of using the cache decorator."""
    # First call - will execute the function and cache the result
    print("First call (not cached):")
    result1 = process_query("JFK", "LAX")
    print(f"Result: {len(result1)} items")
    
    # Second call - will retrieve from cache
    print("\nSecond call (should be cached):")
    result2 = process_query("JFK", "LAX")
    print(f"Result: {len(result2)} items")
    
    # Third call with force_refresh - will bypass cache
    print("\nThird call with force_refresh:")
    result3 = process_query("JFK", "LAX", force_refresh=True)
    print(f"Result: {len(result3)} items")
    
    # Clear the cache for this specific route
    print("\nClearing cache for JFK to LAX...")
    clear_route_cache("JFK", "LAX")
    
    # Fourth call after clearing cache - will execute the function again
    print("\nFourth call (after clearing cache):")
    result4 = process_query("JFK", "LAX")
    print(f"Result: {len(result4)} items")

if __name__ == "__main__":
    # Example of direct cache usage
    print("=== Direct Cache Usage Example ===")
    example_direct_cache_usage()
    
    print("\n=== Cache Decorator Example ===")
    example_decorator_usage() 
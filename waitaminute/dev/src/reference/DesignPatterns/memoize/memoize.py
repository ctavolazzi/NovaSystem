import functools
import time

def memoize(max_size=100, timeout=None):
    def memoize_decorator(func):
        cache = {}
        timestamps = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))

            # Check for expired cache entries
            if timeout:
                for k in list(timestamps.keys()):
                    if time.time() - timestamps[k] > timeout:
                        del cache[k]
                        del timestamps[k]

            if key in cache:
                return cache[key]

            # If cache size limit is reached, remove the oldest item
            if len(cache) >= max_size:
                oldest_key = min(timestamps, key=timestamps.get)
                del cache[oldest_key]
                del timestamps[oldest_key]

            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = time.time()
            return result
        return wrapper
    return memoize_decorator

# Example usage
@memoize(max_size=50, timeout=300)  # 50 items in cache and 5 minutes timeout
def some_function(arg1, arg2, **kwargs):
    # Your function implementation
    return arg1 + arg2  # Replace with actual computation

print(some_function(3, 4, option='value'))

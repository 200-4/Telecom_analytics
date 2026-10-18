# src/retry.py
"""
Retry decorator with exponential backoff for transient failures.
"""

import functools
import time


def retry_with_backoff(max_attempts: int = 3,
                       base_delay: float = 1.0,
                       max_delay: float = 30.0,
                       exceptions: tuple = (Exception,)):
    """
    Retry the wrapped function on the given exceptions.

    Waits base_delay, then 2x, 4x, ... between attempts, capped at max_delay.
    After the last attempt fails, the original exception is raised.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        print(f"❌ {func.__name__} failed after {max_attempts} attempts")
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    print(f"⚠️  {func.__name__} attempt {attempt} failed: {exc}. "
                          f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
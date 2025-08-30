"""
Rate-limited executor for managing concurrent requests to prevent server overload.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Any, List, Optional


class RateLimitedExecutor:
    """
    A ThreadPoolExecutor wrapper that limits the number of concurrent requests
    to prevent server overload while maintaining efficient parallel processing.
    """
    
    def __init__(self, max_workers: int = 16, max_concurrent: int = 8):
        """
        Initialize the rate-limited executor.
        
        Args:
            max_workers: Maximum number of threads in the pool
            max_concurrent: Maximum number of concurrent requests (rate limit)
        """
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = threading.Semaphore(max_concurrent)
    
    def submit_rate_limited(self, fn: Callable, *args, **kwargs):
        """
        Submit a function to be executed with rate limiting.
        
        Args:
            fn: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future object representing the execution
        """
        def rate_limited_wrapper():
            with self.semaphore:  # Acquire rate limit slot
                return fn(*args, **kwargs)
        
        return self.executor.submit(rate_limited_wrapper)
    
    def map_rate_limited(self, fn: Callable, iterable, timeout: Optional[float] = None):
        """
        Execute function over an iterable with rate limiting.
        
        Args:
            fn: Function to execute for each item
            iterable: Items to process
            timeout: Maximum time to wait for completion
            
        Returns:
            List of results in the same order as input
        """
        # Submit all tasks
        futures = [self.submit_rate_limited(fn, item) for item in iterable]
        
        # Collect results in order
        results = []
        for future in futures:
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as e:
                results.append(e)
        
        return results
    
    def map_rate_limited_unordered(self, fn: Callable, iterable, timeout: Optional[float] = None):
        """
        Execute function over an iterable with rate limiting, returning results as they complete.
        
        Args:
            fn: Function to execute for each item
            iterable: Items to process
            timeout: Maximum time to wait for completion
            
        Yields:
            Results as they complete (not in input order)
        """
        # Submit all tasks
        futures = [self.submit_rate_limited(fn, item) for item in iterable]
        
        # Yield results as they complete
        for future in as_completed(futures, timeout=timeout):
            try:
                yield future.result()
            except Exception as e:
                yield e
    
    def shutdown(self, wait: bool = True):
        """Shutdown the executor."""
        self.executor.shutdown(wait=wait)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

# High Concurrency Testing and Configuration

The Text2Everything SDK includes comprehensive high concurrency testing and advanced connection management features to ensure reliable performance under heavy load conditions.

## Overview

The high concurrency test suite validates the system's performance with 32 concurrent requests across all major resource types:

- **Schema Metadata**: Table, dimension, metric, and relationship schemas
- **Contexts**: Business rules and domain knowledge  
- **Golden Examples**: Query-SQL pairs

## Connection Management Features

### Enhanced HTTP Client Configuration

The SDK now includes advanced connection pool management optimized for high-concurrency scenarios and long-running requests:

```python
from text2everything_sdk import Text2EverythingClient

# Standard configuration
client = Text2EverythingClient(
    base_url="https://api.text2everything.com",
    access_token="your-access-token",
    workspace_name="workspaces/dev"
)

# High-concurrency optimized configuration
client = Text2EverythingClient(
    base_url="https://api.text2everything.com",
    access_token="your-access-token",
    workspace_name="workspaces/dev",
    read_timeout=300,              # 5 minutes for long requests
    pool_timeout=600,              # 10 minutes pool timeout
    max_connections=100,           # Higher connection pool
    max_keepalive_connections=20,  # More keep-alive connections
    keepalive_expiry=300,          # 5 minutes keep-alive expiry
    http2=True                     # Enable HTTP/2 for better multiplexing
)
```

### Connection Isolation for Bulk Operations

All bulk operations now support connection isolation to prevent connection conflicts during high concurrency:

```python
# Contexts with connection isolation (default)
contexts = client.contexts.bulk_create(
    project_id=project_id,
    contexts=contexts_data,
    use_connection_isolation=True  # Default: True
)

# Schema metadata with connection isolation
schemas = client.schema_metadata.bulk_create(
    project_id=project_id,
    schema_metadata_list=schemas_data,
    use_connection_isolation=True  # Default: True
)

# Golden examples with connection isolation
examples = client.golden_examples.bulk_create(
    project_id=project_id,
    golden_examples=examples_data,
    use_connection_isolation=True  # Default: True
)
```

## Configuration Parameters

### Client Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `timeout` | 30 | Connection establishment timeout (seconds) |
| `read_timeout` | 180 | Read timeout for long-running requests (seconds) |
| `pool_timeout` | 300 | Connection pool timeout (seconds) |
| `max_connections` | 50 | Maximum total connections in pool |
| `max_keepalive_connections` | 10 | Maximum keep-alive connections |
| `keepalive_expiry` | 300.0 | Keep-alive connection expiry (seconds) |
| `http2` | False | Enable HTTP/2 support |
| `max_retries` | 3 | Maximum number of retries for failed requests |
| `retry_delay` | 1.0 | Initial delay between retries (seconds) |

### Bulk Operation Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `parallel` | True | Execute requests in parallel |
| `max_workers` | min(16, len(items)) | Maximum number of parallel workers |
| `max_concurrent` | 8 | Maximum concurrent requests (rate limiting) |
| `use_connection_isolation` | True | Use isolated HTTP clients per request |

## Test Scenarios

### 1. Individual Resource Testing
- **32 concurrent requests** per resource type
- **Connection isolation enabled** by default
- **Rate limited to 8 concurrent requests** to prevent server overload
- Validates data integrity and performance metrics

### 2. Mixed Resource Testing
- **32 concurrent requests** across all resource types simultaneously
- Tests real-world scenarios with mixed workloads
- Validates cross-resource concurrency handling

### 3. Long-Running Request Support
- **Up to 3+ minute request duration** support
- **Extended timeouts** for complex operations
- **Connection state management** for long-lived requests

## Performance Results

### Test Results Summary

All high concurrency tests achieve **100% success rate**:

#### ✅ Contexts (32 concurrent requests)
- **Success rate**: 32/32 (100%)
- **Average time**: ~1.2 seconds per request
- **Throughput**: ~0.8 requests/second
- **No connection drops**: Zero "Server disconnected" errors

#### ✅ Schema Metadata (32 concurrent requests)  
- **Success rate**: 32/32 (100%)
- **Average time**: ~6.9 seconds per request
- **Throughput**: ~0.1 requests/second
- **Stable operation**: Handles complex schema validation

#### ✅ Golden Examples (32 concurrent requests)
- **Success rate**: 32/32 (100%)  
- **Average time**: ~1.2 seconds per request
- **Throughput**: ~0.9 requests/second
- **Reliable execution**: Consistent performance

## Running High Concurrency Tests

### Individual Resource Tests

```bash
# Test contexts high concurrency
python run_tests.py --tests high_concurrency_contexts

# Test schema metadata high concurrency  
python run_tests.py --tests high_concurrency_schema_metadata

# Test golden examples high concurrency
python run_tests.py --tests high_concurrency_golden_examples
```

### All High Concurrency Tests

```bash
# Run all high concurrency tests
python run_tests.py --tests "high_concurrency_contexts,high_concurrency_schema_metadata,high_concurrency_golden_examples"
```

### List Available Tests

```bash
# See all available test suites
python run_tests.py --list-tests
```

## Best Practices for High Concurrency

### 1. Connection Configuration
- Use **connection isolation** for bulk operations (enabled by default)
- Configure **appropriate timeouts** based on expected request duration
- Set **reasonable connection pool limits** based on your infrastructure

### 2. Rate Limiting
- Use the **max_concurrent parameter** to control server load
- Start with **8 concurrent requests** and adjust based on server capacity
- Monitor server performance and adjust limits accordingly

### 3. Error Handling
- The SDK includes **automatic retry logic** with exponential backoff
- **Connection isolation** prevents cascading failures
- **Enhanced error handling** for protocol-level issues

### 4. Monitoring
- Monitor **request success rates** and **response times**
- Watch for **connection pool exhaustion** warnings
- Track **server resource utilization** during high load

## Troubleshooting

### Common Issues and Solutions

#### Connection Drops
- **Solution**: Connection isolation is enabled by default
- **Verification**: Check `use_connection_isolation=True` in bulk operations

#### Timeout Errors
- **Solution**: Increase `read_timeout` for long-running requests
- **Example**: `read_timeout=300` for 5-minute operations

#### Rate Limiting
- **Solution**: Reduce `max_concurrent` parameter
- **Example**: `max_concurrent=4` for lower server load

#### Memory Usage
- **Solution**: Reduce `max_connections` and `max_keepalive_connections`
- **Example**: `max_connections=25, max_keepalive_connections=5`

## Advanced Configuration Examples

### High-Throughput Configuration
```python
client = Text2EverythingClient(
    base_url="https://api.text2everything.com",
    access_token="your-access-token",
    workspace_name="workspaces/dev",
    max_connections=200,
    max_keepalive_connections=50,
    max_concurrent=16,  # Higher concurrency
    http2=True
)
```

### Long-Running Operations Configuration
```python
client = Text2EverythingClient(
    base_url="https://api.text2everything.com", 
    api_key="your-api-key",
    read_timeout=600,    # 10 minutes
    pool_timeout=900,    # 15 minutes
    keepalive_expiry=600 # 10 minutes
)
```

### Conservative Configuration
```python
client = Text2EverythingClient(
    base_url="https://api.text2everything.com",
    access_token="your-access-token", 
    workspace_name="workspaces/dev", 
    max_connections=25,
    max_keepalive_connections=5,
    max_concurrent=4,    # Lower concurrency
    use_connection_isolation=True
)
```

## Connection Isolation Technical Details

### How It Works
- Each concurrent request in bulk operations uses an **isolated HTTP client**
- **Zero keep-alive connections** in isolated clients prevent state conflicts
- **Automatic cleanup** ensures no connection leaks
- **Fallback to shared pool** when isolation is disabled

### When to Use
- **High concurrency scenarios** (default behavior)
- **Long-running requests** that might timeout
- **Mixed workload environments** with varying request patterns
- **Production environments** requiring maximum reliability

### When to Disable
- **Low concurrency scenarios** (< 4 concurrent requests)
- **Resource-constrained environments** with limited memory
- **Testing scenarios** where you want to test shared connection pools
- **Debugging connection pool behavior**

The Text2Everything SDK's high concurrency features provide enterprise-grade reliability and performance for demanding production environments.

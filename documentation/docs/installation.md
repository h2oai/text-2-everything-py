---
title: Installation
---

This guide helps you install the **Python SDK for Text2Everything** in a clean environment, verify the installation, and find common fixes.

## Prerequisites
**Python 3.9+**: The SDK targets CPython 3.9 or newer.

## Install options
Choose one of the supported methods to install the SDK.

### Step 1: Local wheel (current builds)
Install from the wheel bundled with this repository or your build pipeline.
```bash
pip install dist/text2everything_sdk-0.1.2-py3-none-any.whl
```

### Step 2: Using PyPI (Future)
```bash
pip install text2everything-sdk
```

> Tip: Use a virtual environment (for example, `python -m venv .venv && source .venv/bin/activate`) to isolate dependencies.

## Verify installation
Run this snippet to confirm the package is importable and report its version.
```python
import text2everything_sdk as t2e
print(t2e.__version__)
```

If a version prints without error, the SDK is installed correctly.

## Next steps
After installing, configure the client and try a minimal working example.
- Configure authentication and timeouts in [Configuration](./configuration.md)
- Run your first example in [Quickstart](./quickstart.md)

## Troubleshooting
Use these common fixes if installation or imports fail.
- Ensure Python 3.9+
- If behind a proxy, set `HTTP_PROXY`/`HTTPS_PROXY`
- If using an internal package index, set `PIP_INDEX_URL`
- If `pip` fails TLS/SSL checks, update `certifi` or your OS trust store



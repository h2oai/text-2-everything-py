---
title: Installation
---

## Install from PyPI (recommended)

```bash
pip install h2o-text-2-everything
```

[PyPI](https://pypi.org/project/h2o-text-2-everything/) hosts the package, which includes all SDK dependencies. Use a virtual environment to keep dependencies isolated, for example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install h2o-text-2-everything
```

## Install from a local wheel (optional)

If you are testing a pre-release build, install the wheel artifact instead:

```bash
pip install dist/h2o_text_2_everything-<version>-py3-none-any.whl
```
:::info note
Replace `<version>` with the filename of the wheel you want to test.
:::

## Troubleshooting

### Python version errors

If you encounter version-related errors, verify that Python 3.9 or higher is installed:

```bash
python --version
```

### Proxy configuration

If you are behind a proxy, configure the `HTTP_PROXY` and `HTTPS_PROXY` environment variables before installation:

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8080"
pip install h2o-text-2-everything
```

### Check for updates

To verify you have the latest version, check the [Releases](https://github.com/h2oai/text-2-everything-py/releases) page or [PyPI](https://pypi.org/project/h2o-text-2-everything/).

---
title: Installation
---

## Install from PyPI (recommended)

```bash
pip install h2o-text-2-everything
```

The package is published on [PyPI](https://pypi.org/project/h2o-text-2-everything/) and includes all SDK dependencies. Use a virtual environment to keep dependencies isolated, for example:

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

Replace `<version>` with the filename of the wheel you want to test.

## Troubleshooting

- **Python Version**: Ensure Python 3.9 or higher is installed
- **Proxy Settings**: If behind a proxy, set `HTTP_PROXY`/`HTTPS_PROXY` environment variables
- **Latest Version**: Check the [Releases](https://github.com/h2oai/text-2-everything-py/releases) page or PyPI for the newest version

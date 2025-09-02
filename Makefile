.PHONY: docs docs-build docs-serve venv

VENV_BIN=.venv/bin
PY=$(VENV_BIN)/python
PIP=$(VENV_BIN)/pip
MKDOCS=$(VENV_BIN)/mkdocs

venv:
	@test -d .venv || python3 -m venv .venv
	@$(PIP) install --upgrade pip >/dev/null
	@$(PIP) install -r requirements-dev.txt >/dev/null
	@$(PIP) install -e . >/dev/null

# Build static site into site/
docs-build: venv
	@$(MKDOCS) build

pdfs: venv
	@$(PY) scripts/build_docs_pdfs.py

# Run local dev server on :8000
docs: venv
	@echo "Serving docs at http://127.0.0.1:8000"
	@$(MKDOCS) serve -a 127.0.0.1:8000

# Alias
docs-serve: docs

.PHONY: venv

VENV_BIN=.venv/bin
PY=$(VENV_BIN)/python
PIP=$(VENV_BIN)/pip

venv:
	@test -d .venv || python3 -m venv .venv
	@$(PIP) install --upgrade pip >/dev/null
	@$(PIP) install -r requirements-dev.txt >/dev/null
	@$(PIP) install -e . >/dev/null

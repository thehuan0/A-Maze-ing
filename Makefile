VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

MAIN_FILE = a_maze_ing.py
CONFIG_FILE = config.txt
REQUIREMENTS = requirements.txt

# Rule to build the package
PACKAGE_RULE = python3 -m build

all: install run

install: $(VENV)/bin/activate

$(VENV)/bin/activate: $(REQUIREMENTS)
	python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
	@$(PIP) install -e . 
	@touch $(VENV)/bin/activate

run: install
	$(PYTHON) $(MAIN_FILE) $(CONFIG_FILE)

# Lint rule
lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# Re-generate the package
package: install
	$(PYTHON) -m build

clean:
	@rm -rf __pycache__ .mypy_cache $(VENV) build dist *.egg-info

.PHONY: all lint clean run package
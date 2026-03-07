.PHONY: install run debug clean lint lint-strict

PYTHON ?= python3
PIP ?= pip
MAIN ?= code/a_maze_ing.py

install:
    @if [ -f requirements.txt ]; then \
        $(PIP) install -r requirements.txt; \
    else \
        echo "No requirements.txt found. Skipping dependency installation."; \
    fi

run:
    $(PYTHON) $(MAIN)

debug:
    $(PYTHON) -m pdb $(MAIN)

clean:
    find . -type d -name "__pycache__" -prune -exec rm -rf {} +
    find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete

lint:
    flake8 .
    mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
    flake8 .
    mypy . --strict
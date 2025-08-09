.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install dependencies"
	@echo "  update           Update dependencies"
	@echo ""
	@echo "Development:"
	@echo "  lint             Run linter and formatter"
	@echo "  test             Run tests"
	@echo "  format           Run code formatter"
	@echo "  tests            Run tests (alias)"
	@echo "  coverage         Generate coverage report"
	@echo ""
	@echo "Design Assistant:"
	@echo "  design-app       Design a new application interactively"
	@echo "  design-feature   Design a new feature interactively"
	@echo "  simulate         Run automated simulation with learning"
	@echo "  knowledge-stats  View learning system statistics"

.PHONY: install
install:
	@echo "Installing dependencies"
	uv venv
	uv sync --extra dev
	uv run playwright install

.PHONY: update
update:
	@echo "Updating dependencies"
	uv lock --upgrade
	uv sync --extra dev

.PHONY: lint
lint:
	@echo "Running linter and formatter"
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: format
format:
	@echo "Formatting code"
	uv run ruff format .

.PHONY: test
test:
	@echo "Running tests with cleanup verification"
	# Run all tests
	uv run pytest tests/ -v --tb=short

.PHONY: coverage
coverage:
	@echo "Generating coverage report"
	uv run pytest --cov=src --cov-report term-missing

.PHONY: publish
publish:
	@echo "Publishing package to PyPI"
	uv build
	uv publish

.PHONY: design-app
design-app:
	@echo "Starting interactive application design assistant..."
	uv run python -m claude_code_designer.cli app

.PHONY: design-feature
design-feature:
	@echo "Starting interactive feature design assistant..."
	uv run python -m claude_code_designer.cli feature

.PHONY: simulate
simulate:
	@echo "Running automated design simulation with learning..."
	uv run python -m claude_code_designer.cli simulate --cycles 5 --enable-learning

.PHONY: knowledge-stats
knowledge-stats:
	@echo "Displaying learning system knowledge statistics..."
	uv run python -m claude_code_designer.cli knowledge-stats

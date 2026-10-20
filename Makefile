
.PHONY: all
all:
	@echo "Run my targets individually!"

.PHONY: dev
dev:
	uv sync --locked

.PHONY: lint
lint:
	uv run --locked --dev ruff format --check action.py
	uv run --locked --dev ruff check action.py
	uv run --locked --dev mypy action.py

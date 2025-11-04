
.PHONY: all
all:
	@echo "Run my targets individually!"

.venv/pyvenv.cfg: requirements/dev.txt
	setup/create-venv.sh .venv
	. ./.venv/bin/activate && \
	uv pip install -r requirements/dev.txt

.PHONY: dev
dev: .venv/pyvenv.cfg

.PHONY: lint
lint: .venv/pyvenv.cfg action.py
	. ./.venv/bin/activate && \
	ruff format --diff action.py && \
	ruff check action.py && \
	mypy action.py

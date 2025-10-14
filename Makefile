
.PHONY: all
all:
	@echo "Run my targets individually!"

.venv/pyvenv.cfg: requirements/dev.txt requirements/main.txt
	uv venv
	. ./.venv/bin/activate && \
	uv pip install -r requirements/main.txt -r requirements/dev.txt

.PHONY: dev
dev: .venv/pyvenv.cfg

.PHONY: lint
lint: .venv/pyvenv.cfg action.py
	. ./.venv/bin/activate && \
	black action.py && \
	isort action.py && \
	mypy action.py && \
	flake8 --max-line-length 100 action.py

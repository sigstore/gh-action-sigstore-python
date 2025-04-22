
.PHONY: all
all:
	@echo "Run my targets individually!"

.PHONY: requirements
requirements: requirements/main.txt requirements/dev.txt

requirements/%.txt: requirements/%.in
	uv pip compile --generate-hashes --prerelease=allow --output-file=$@ $<

env/pyvenv.cfg: requirements/dev.txt requirements/main.txt
	uv venv
	uv pip install -r requirements/main.txt -r requirements/dev.txt

.PHONY: dev
dev: env/pyvenv.cfg

.PHONY: lint
lint: env/pyvenv.cfg action.py
	. ./.venv/bin/activate && \
	black action.py && \
	isort action.py && \
	mypy action.py && \
	flake8 --max-line-length 100 action.py

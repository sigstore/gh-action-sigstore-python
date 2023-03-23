.PHONY: all
all:
	@echo "Run my targets individually!"

env/pyvenv.cfg: dev-requirements.txt
	python3 -m venv env
	./env/bin/python -m pip install --upgrade pip
	./env/bin/python -m pip install --requirement dev-requirements.txt

.PHONY: dev
dev: env/pyvenv.cfg

.PHONY: lint
lint: env/pyvenv.cfg action.py
	. ./env/bin/activate && \
	black action.py && \
	isort action.py && \
	mypy action.py && \
	flake8 --max-line-length 100 action.py

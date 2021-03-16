.PHONY: dev format lint test build release

dev:
	pip install --upgrade pip poetry
	poetry install

format:
	@echo "skipped"

lint: format
	poetry run flake8 piqe_ocp_lib/*

test:
	poetry run pytest

build: lint test
	poetry build

release: build
	poetry config pypi-token.pypi ${PYPI_TOKEN}
	poetry publish --no-interaction

.PHONY: dev format lint test build release-test release-prod

dev:
	pip install --upgrade pip poetry
	poetry install

format:
	poetry run isort piqe_ocp_lib/
	poetry run black piqe_ocp_lib/

lint: format
	poetry run flake8 piqe_ocp_lib/*

test:
	poetry run pytest

build: lint test
	poetry build

release-test:
	poetry config repositories.testpypi https://test.pypi.org/simple
	poetry config pypi-token.pypi ${PYPI_TEST_TOKEN}
	poetry publish --repository testpypi -n

release-prod:
	poetry config pypi-token.pypi ${PYPI_TOKEN}
	poetry publish --no-interaction

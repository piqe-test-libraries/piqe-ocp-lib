.PHONY = dev lint test

dev:
	pip install .[dev]

lint:
	flake8 piqe_ocp_lib/  --show-source --max-line-length=120

test:
	pytest -sv -m $(TYPE)

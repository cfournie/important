all: install test lint

install:
	pip install -e .[test]

test:
	py.test -vv --cov=important tests/

lint:
	flake8 --ignore D .

all: install test lint

install:
	pip install '.[test]'

test:
	py.test -vv --cov=important tests/

lint:
	flake8 --ignore D .

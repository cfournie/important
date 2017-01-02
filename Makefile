all: install test lint

install:
	pip install -e .
	pip install -r dev_requirements.txt

test: install
	py.test -vv --cov=important tests/
	important -v --requirements requirements.txt --constraints constraints.txt .

coverage:
	py.test -vv --cov=important --cov-report html tests/

autolint:
	pip install autopep8
	autopep8 --in-place --aggressive --aggressive *.py
	autopep8 --in-place --aggressive --aggressive **/*.py

lint:
	flake8 --ignore D .

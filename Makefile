all: install test lint

install:
	pip install -e .
	pip install -r dev_requirements.txt

test:
	py.test -vv --cov=important tests/
	important -v --requirements requirements.txt --constraints constraints.txt .

coverage:
	py.test -vv --cov=important --cov-report html tests/

lint:
	flake8 --ignore D .

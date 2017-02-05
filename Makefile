PYTHON_VERSION := `python -c 'import sys; print(sys.version_info.major)'`

all: install test lint

install:
	pip install -e .
	@if [ "$(PYTHON_VERSION)" = "2" ]; then pip install -r python27_requirements.txt; fi
	pip install -r dev_requirements.txt
test: install
	py.test -vv --cov=important tests/
	important -v

coverage:
	py.test -vv --cov=important --cov-report html tests/

autolint:
	pip install autopep8
	autopep8 --in-place --aggressive --aggressive *.py
	autopep8 --in-place --aggressive --aggressive **/*.py

lint:
	flake8 --ignore D .

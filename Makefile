python_version := `python -c 'import sys; print(sys.version_info.major)'`
python_files := find . -path '*/.*' -prune -o -name '*.py' -print0

all: install test lint

clean:
		find . \( -name '*.pyc' -o -name '*.pyo' -o -name '*~' \) -print -delete >/dev/null
		find . -name '__pycache__' -exec rm -rvf '{}' + >/dev/null
		rm -fr *.egg-info

install:
		pip install -e .
		@if [ "$(python_version)" = "2" ]; then pip install -r python27_requirements.txt; fi
		pip install -r dev_requirements.txt

test: clean install
		py.test -vv --cov=important tests/
		important -v

coverage:
		py.test -vv --cov=important --cov-report html tests/

autopep8:
		@echo 'Auto Formatting...'
		@$(python_files) | xargs -0 autopep8 --max-line-length 120 --jobs 0 --in-place --aggressive

lint:
		flake8 --ignore D .
		@echo 'Linting...'
		@pylint --rcfile=pylintrc important tests
		@flake8

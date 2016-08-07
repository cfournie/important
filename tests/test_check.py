import pytest
from important.parse import parse_requirements
from important.check import check_unused_requirements, \
    frequency_count_imports, check_import_frequencies


def test_unused_requirements(python_file_imports, tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
        unused
        os
        csv
        parser'''.strip())
    requirements = parse_requirements(str(requirements_file))
    assert check_unused_requirements(python_file_imports, requirements) == \
        set(['unused'])


def test_frequency_count_imports(python_file_imports):
    assert frequency_count_imports(python_file_imports) == {
        'collections': 3,
        'copy': 3,
        'csv': 3,
        'enum': 3,
        'math': 3,
        'os': 9,
        'os.path': 6,
        'parser': 3,
        're': 3,
        'sys': 3,
        'time': 3
    }


def test_check_import_frequencies(tmpdir, python_file_imports):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
        unused==0
        other_unused==0
        os<6
        os.path<6
        enum<10
        csv>1
        re>1,<=3'''.strip())
    requirements = parse_requirements(str(requirements_file))
    assert check_import_frequencies(python_file_imports, requirements) == {
        'os': 9,
        'os.path': 6
    }

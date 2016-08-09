import pytest
from pip._vendor.packaging.specifiers import SpecifierSet
from important.parse import parse_requirements
from important.check import check_unused_requirements, \
    frequency_count_imports, check_import_frequencies


def test_unused_requirements(python_file_imports, requirements_file):
    requirements = parse_requirements(requirements_file)
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


def test_check_import_frequencies(python_file_imports, constraints_file):
    requirements = parse_requirements(constraints_file)
    assert check_import_frequencies(python_file_imports, requirements) == {
        'os': (SpecifierSet('<6'), 9),
        'os.path': (SpecifierSet('<6'), 6),
    }

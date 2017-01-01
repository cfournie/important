from pip._vendor.packaging.specifiers import SpecifierSet
from important.parse import parse_requirements
from important.check import check_unused_requirements, \
    frequency_count_imports, check_import_frequencies


def test_unused_requirements(
        python_file_imports,
        requirements_file_one_unused):
    requirements = parse_requirements(requirements_file_one_unused)
    unused_requirements = check_unused_requirements(
        python_file_imports, requirements)
    assert set(unused_requirements) == {'unused'}


def test_frequency_count_imports(python_file_imports, import_name):
    assert frequency_count_imports(python_file_imports) == {
        import_name: 3,
        'collections': 3,
        'copy': 6,
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


def test_check_import_frequencies(
        python_file_imports,
        constraints_file_package_disallowed,
        package_name):
    requirements = parse_requirements(constraints_file_package_disallowed)
    assert check_import_frequencies(python_file_imports, requirements) == {
        'os': (SpecifierSet('<6'), 9),
        'os.path': (SpecifierSet('<6'), 6),
        package_name: (SpecifierSet('==0'), 3),
    }

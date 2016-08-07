import pytest

from requirements.check import check_unused_requirements, \
    frequency_count_imports, _get_module_containing_dir


def test_unused_requirements(python_file_imports):
    requirements = ['unused', 'os', 'csv', 'parser']
    assert check_unused_requirements(python_file_imports, requirements) == \
        set(['unused'])

def test_get_module_containing_dir():
    assert _get_module_containing_dir('os') == 'lib/python3.4'
    assert _get_module_containing_dir('csv') == 'lib/python3.4'
    assert _get_module_containing_dir('urllib') == 'lib/python3.4'
    assert _get_module_containing_dir('unknown') == 'lib/python3.4'

@pytest.mark.xfail
def test_frequency_count_imports(python_file_imports):
    assert frequency_count_imports(python_file_imports) == ({

    }, {})

from requirements.check import check_unused_requirements


def test_unused_requirements(python_file_imports):
    requirements = ['unused', 'os', 'csv', 'parser']
    assert check_unused_requirements(python_file_imports, requirements) == \
        set(['unused'])

import pytest
from important.parse import import_statement


@pytest.fixture
def python_imports():
    return [
        ('collections', 2, 0),
        ('math', 3, 0),
        ('os', 4, 0),
        ('copy', 5, 0),
        ('re', 6, 0),
        ('time', 6, 0),
        ('sys', 6, 0),
        ('os.path', 7, 0),
        ('os.path', 8, 0),
        ('parser', 13, 4),
        ('enum', 16, 4),
        ('csv', 19, 8),
    ]


@pytest.fixture
def python_file_imports(python_imports):
    def create_results(filepath):
        return list(map(
            lambda x: import_statement(x[0], filepath, x[1], x[2]),
            python_imports
        ))
    items = create_results('test.py')
    items.extend(create_results('testdir/test.py'))
    items.extend(create_results('testdir/testfile'))
    return items

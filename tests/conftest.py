import pytest
from important.parse import import_statement


@pytest.fixture
def python_imports():
    return [
        ('collections', 2),
        ('math', 3),
        ('os', 4),
        ('copy', 5),
        ('re', 6),
        ('time', 6),
        ('sys', 6),
        ('os.path', 7),
        ('os.path', 8),
        ('parser', 13),
        ('enum', 16),
        ('csv', 19),
    ]


@pytest.fixture
def python_file_imports(python_imports):
    def create_results(filepath):
        return list(map(
            lambda x: import_statement(x[0], filepath, x[1]),
            python_imports
        ))
    items = create_results('test.py')
    items.extend(create_results('testdir/test.py'))
    items.extend(create_results('testdir/testfile'))
    return items

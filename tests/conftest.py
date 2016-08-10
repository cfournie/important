import pytest
from important.parse import Import


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
            lambda x: Import(x[0], filepath, x[1], x[2]),
            python_imports
        ))
    items = create_results('test.py')
    items.extend(create_results('testdir/test.py'))
    items.extend(create_results('testdir/testfile'))
    return items


@pytest.fixture
def python_source():
    return '''
#!/usr/bin/env python
from collections import defaultdict
from math import abs as absolute
import os
import copy as duplicate
import re, time, sys
import os.path
from os.path import exists, join

print("test")

def func():
    import parser

class A(object):
    import enum

    def method(self):
        import csv
'''.strip()


@pytest.fixture
def python_source_file(tmpdir, python_source):
    python_source_file = tmpdir.join('test.py')
    python_source_file.write(python_source)
    return str(python_source_file)


@pytest.fixture
def python_source_dir(tmpdir, python_source):
    python_source_dir = tmpdir.mkdir('dir')
    python_source_dir.join('test1.py').write(python_source)
    python_source_dir.join('test2.py').write(python_source)
    python_source_subdir = tmpdir.mkdir('subdir')
    python_source_subdir.join('test3.py').write(python_source)
    return str(python_source_dir)


@pytest.fixture
def requirements_file(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
unused
os
csv
parser'''.strip())
    return str(requirements_file)


@pytest.fixture
def constraints_file(tmpdir):
    constraints_file = tmpdir.join('constraints.txt')
    constraints_file.write('''
unused==0
other_unused==0
os<6
os.path<6
enum<10
csv>1
re>1,<=3'''.strip())
    return str(constraints_file)

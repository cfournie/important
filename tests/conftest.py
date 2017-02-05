# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import stat
import sys

from important.parse import Import


ENCODING = 'utf-8' if sys.version_info > (3, 0) else 'utf8'

IMPORT_STATEMENT_TO_IMPORT = {
    'import dns': 'dns',
    'import IPy': 'IPy',
    'from IPy import IP': 'IPy',
    'import numpy': 'numpy',
    'import numpy as np': 'numpy',
    'import yaml': 'yaml',
    'from bs4 import BeautifulSoup': 'bs4',
    'import pylab': 'pylab',
    'import matplotlib.pyplot as plt': 'matplotlib.pyplot',
    'import cssutils': 'cssutils',
}

# Add Python 2.7 and lower tests
if sys.version_info < (3, 0):
    IMPORT_STATEMENT_TO_IMPORT.update({
        'import wsgiref': 'wsgiref',
    })

IMPORT_TO_PACKAGE = {
    # package installed with differing name ('dns' folder)
    'dns': 'dnspython',
    'IPy': 'IPy',  # case sensitive package name installed as file ('IPy.py')
    'numpy': 'numpy',  # package with C extensions
    'yaml': 'pyyaml',  # package installed with differing name
    'bs4': 'beautifulsoup4',  # package installed with differing name
    'matplotlib': 'matplotlib',
    'cssutils': 'cssutils',
    'pylab': 'matplotlib',
    'matplotlib.pyplot': 'matplotlib',
}

# Add Python 2.7 and lower tests
if sys.version_info < (3, 0):
    IMPORT_TO_PACKAGE.update({
        'wsgiref': 'wsgiref',
    })


@pytest.fixture(params=IMPORT_STATEMENT_TO_IMPORT.items())
def import_statement_and_import(request):
    return request.param


@pytest.fixture
def import_statement(import_statement_and_import):
    return import_statement_and_import[0]


@pytest.fixture
def import_name(import_statement_and_import):
    return import_statement_and_import[1]


@pytest.fixture
def package_name(import_name):
    return IMPORT_TO_PACKAGE[import_name]


@pytest.fixture
def python_source(import_statement):
    return '''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import defaultdict
from math import abs as absolute
import os
import copy
import copy as duplicate
{import_statement}
import re, time, sys
import os.path
from os.path import exists, join

print("test😀")

def func():
    import parser

class A(object):
    import enum

    def method(self):
        import csv
'''.strip().format(import_statement=import_statement)


@pytest.fixture
def python_imports(import_name):
    return [
        ('__future__', 3, 0),
        ('collections', 4, 0),
        ('math', 5, 0),
        ('os', 6, 0),
        ('copy', 7, 0),
        ('copy', 8, 0),
        (import_name, 9, 0),
        ('re', 10, 0),
        ('time', 10, 0),
        ('sys', 10, 0),
        ('os.path', 11, 0),
        ('os.path', 12, 0),
        ('parser', 17, 4),
        ('enum', 20, 4),
        ('csv', 23, 8),
    ]


@pytest.fixture
def python_files_parsed():
    return ('scriptfile', 'test1.py', 'subdir/test3.py')


@pytest.fixture
def python_file_imports(python_imports, import_name, python_files_parsed):
    def create_results(filepath):
        return list(map(
            lambda x: Import(x[0], filepath, x[1], x[2]),
            python_imports
        ))
    items = []
    for python_file_parsed in python_files_parsed:
        items.extend(create_results(python_file_parsed))
    return items


@pytest.fixture
def python_source_file(tmpdir, python_source):
    python_source_file = tmpdir.join('test.py')
    python_source_file.write_text(python_source, encoding=ENCODING)
    return str(python_source_file)


@pytest.fixture
def binary_file(tmpdir):
    binary_file = tmpdir.join('bad')
    with open(str(binary_file), 'wb') as fh:
        fh.write(bytearray.fromhex('FFFF FFFF'))
    return str(binary_file)


@pytest.fixture
def __python_source_dir__(tmpdir, python_source):
    executable_file_mode = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH \
        | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH

    # Create a set of python files and a script file within
    # the base or other subdirectories that should be parsed
    python_source_dir = tmpdir.mkdir('dir')
    python_source_dir.join('test1.py').write_text(
        python_source, encoding=ENCODING)
    python_scriptfile = python_source_dir.join('scriptfile')
    python_scriptfile.write_text(python_source, encoding=ENCODING)
    python_scriptfile.chmod(executable_file_mode)
    python_source_subdir = python_source_dir.mkdir('subdir')
    python_source_subdir.join('test3.py').write_text(
        python_source, encoding=ENCODING)

    # Add file without shebang, but the correct permissions, that shouldn't be
    # parsed
    randomfile = python_source_dir.join('random😀file')
    randomfile.write_text(
        '\n'.join(python_source.split('\n')[1:]), encoding=ENCODING)
    randomfile.chmod(executable_file_mode)

    # Add file with shebang but wrong permissions that shouldn't be parsed
    python_source_dir.join('otherrandomfile').write_text(
        python_source, encoding=ENCODING)

    return python_source_dir


@pytest.fixture
def python_source_dir(__python_source_dir__):
    return str(__python_source_dir__)


@pytest.fixture
def python_excluded_dir(__python_source_dir__):
    # Create a directory intended to be excluded
    python_excluded_dir = __python_source_dir__.mkdir('excluded')
    python_excluded_dir.join('test4.py').write(python_source)
    return str(python_excluded_dir)


@pytest.fixture
def python_excluded_file(__python_source_dir__):
    python_excluded_file = __python_source_dir__.join('excluded.py')
    python_excluded_file.write(python_source)
    return str(python_excluded_file)


@pytest.fixture
def exclusions(python_excluded_file, python_excluded_dir):
    return [python_excluded_file, python_excluded_dir]


@pytest.fixture
def requirements_file(tmpdir, package_name):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
os
csv
parser
{package_name}'''.strip().format(
        package_name=package_name
    ))
    return str(requirements_file)


@pytest.fixture
def requirements_file_one_unused(requirements_file):
    with open(requirements_file, 'a') as fh:
        fh.write('\nunused')
    return requirements_file


@pytest.fixture
def constraints_file_package_disallowed(tmpdir, package_name):
    constraints_file = tmpdir.join('constraints.txt')
    constraints_file.write('''
unused==0
other_unused==0
os<6
os.path<6
{package_name}==0
enum<10
csv>1
other
re>1,<=3'''.strip().format(
        package_name=package_name
    ))
    return str(constraints_file)


@pytest.fixture
def constraints_file(tmpdir, package_name):
    constraints_file = tmpdir.join('constraints.txt')
    constraints_file.write('''
unused==0
other_unused==0
os<=9
os.path<=6
{package_name}<=6
enum<10
csv>1
    re>1,<=3'''.strip().format(
        package_name=package_name
    ))
    return str(constraints_file)

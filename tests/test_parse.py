import pytest
from requirements.parse import _imports, parse_file_imports, parse_dir_imports, \
    parse_requirements, import_statement, RE_SHEBANG
import stat


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


def test_imports(python_source, python_imports):
    assert list(_imports(python_source)) == python_imports


def test_file_imports(tmpdir, python_source, python_imports):
    sourcefile = tmpdir.join('test.py')
    sourcefile.write(python_source)
    assert list(parse_file_imports(str(sourcefile.realpath()))) == \
        python_imports


def test_dir_imports(tmpdir, python_source, python_file_imports):
    file_mode = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH \
                | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH

    # Create a set of python files and a script file within
    # the base or other subdirectories that should be parsed
    tmpdir.join('test.py').write(python_source)
    dirpath = tmpdir.ensure('testdir', dir=True)
    dirpath.join('test.py').write(python_source)
    scriptfile = dirpath.join('testfile')
    scriptfile.write(python_source)
    scriptfile.chmod(file_mode)

    # Add file without shebang that shouldn't be parsed
    randomfile = dirpath.join('randomfile')
    randomfile.write('\n'.join(python_source.split('\n')[1:]))
    randomfile.chmod(file_mode)

    # Add file with shebang but wrong mode that shouldn't be parsed
    dirpath.join('otherrandomfile').write(python_source)

    assert list(parse_dir_imports(str(tmpdir))) == python_file_imports


def test_re_shebang():
    assert RE_SHEBANG.match('#!/usr/bin/env python')
    assert RE_SHEBANG.match('#!/usr/bin/env python2')
    assert RE_SHEBANG.match('#!/usr/bin/env python3')
    assert RE_SHEBANG.match('#! /usr/bin/python')
    assert RE_SHEBANG.match('#!/usr/bin/python')
    assert RE_SHEBANG.match('#!/usr/local/bin/python')
    assert RE_SHEBANG.match('#!python')
    assert not RE_SHEBANG.match('#!/usr/bin/env bash')
    assert not RE_SHEBANG.match('#!/bin/bash')
    assert not RE_SHEBANG.match('#!/bin/sh')
    assert not RE_SHEBANG.match('#!/bin/sh - ')


def test_requirements(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
pkg1
pkg2
pkg3>=1.0,<=2.0
git+https://myvcs.com/some_dependency@sometag#egg=SomeDependency
    '''.strip())
    assert list(parse_requirements(str(requirements_file))) == [
        'pkg1', 'pkg2', 'pkg3', 'somedependency']


def test_requirements_without_name(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
git+https://myvcs.com/some_dependency@sometag
    '''.strip())
    with pytest.raises(ValueError) as excinfo:
        list(parse_requirements(str(requirements_file)))
    assert str(excinfo.value) == \
        'A requirement lacks a name (e.g. no `#egg` on a `file:` path)'


def test_requirements_editable(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
-e git+https://myvcs.com/some_dependency@sometag#egg=SomeDependency
    '''.strip())
    with pytest.raises(ValueError) as excinfo:
        list(parse_requirements(str(requirements_file)))
    assert str(excinfo.value) == \
        'Cannot parse SomeDependency: editable projects unsupported'


def test_requirements_file_link(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
file:///path/to/your/lib/project#egg=MyProject
    '''.strip())
    with pytest.raises(ValueError) as excinfo:
        list(parse_requirements(str(requirements_file)))
    assert str(excinfo.value) == \
        'Cannot parse MyProject: file-specified projects unsupported'

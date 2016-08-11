import pytest
from important.parse import _imports, parse_file_imports, parse_dir_imports, \
    parse_requirements, Import, RE_SHEBANG


def test_imports(python_source, python_imports):
    assert list(_imports(python_source)) == python_imports


def test_file_imports(python_source_file, python_imports):
    assert list(parse_file_imports(python_source_file)) == \
           list(map(lambda i: Import(i[0], 'test.py', i[1], i[2]),
                    python_imports))


def test_dir_imports(tmpdir, python_source_dir, python_file_imports):
    print(list(parse_dir_imports(python_source_dir)))
    assert list(parse_dir_imports(python_source_dir)) == python_file_imports


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
    assert [requirement.name for requirement in
            parse_requirements(str(requirements_file))] == [
            'pkg1', 'pkg2', 'pkg3', 'SomeDependency']


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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import pytest
import stat
import sys

from important.parse import _imports, parse_file_imports, parse_dir_imports, \
    parse_requirements, Import, RE_SHEBANG, _is_script, \
    translate_requirement_to_module_names

try:
    from unittest.mock import Mock
except:
    from mock import Mock

ENCODING = 'utf-8' if sys.version_info > (3, 0) else 'utf8'


def test_imports(python_source, python_imports):
    assert list(_imports(python_source.encode(ENCODING), 'filename.py')) == \
        python_imports


def test_file_imports(python_source_file, python_imports):
    assert list(parse_file_imports(python_source_file)) == \
        list(map(lambda i: Import(i[0], 'test.py', i[1], i[2]),
                 python_imports))


def test_file_imports_with_syntax_error(mocker, python_source_file):
    logger = Mock()
    mocker.patch('important.parse.logger', logger)

    # Alter file so that it won't compile
    with open(python_source_file, 'a') as fh:
        fh.write('not a valid Python statement')

    # Attempt to parse and assert that it logged a warning
    list(parse_file_imports(python_source_file))
    logger.warning.assert_called_with(
        'Skipping {filename} due to syntax error: {error}'.format(
            filename=python_source_file,
            error='invalid syntax (test.py, line 23)'
        )
    )


def test_file_imports_with_utf8_encoding(mocker, tmpdir):
    python_source_file = str(tmpdir.join('utf8.py'))
    with codecs.open(python_source_file, mode='w', encoding='utf8') as fh:
        fh.write(
            '''# -*- coding: utf-8 -*-
import os

print('uʍop ǝpısdn')'''
        )

    logger = Mock()
    mocker.patch('important.parse.logger', logger)

    # Attempt to parse and assert that it logged a warning
    assert list(parse_file_imports(python_source_file)) == [
        Import(module='os', filename='utf8.py', lineno=2, col_offset=0)
    ]

    logger.warning.assert_not_called()


def test_file_imports_binary_file(mocker, binary_file):
    logger = Mock()
    mocker.patch('important.parse.logger', logger)

    # Attempt to parse and assert that it logged a warning
    list(parse_file_imports(binary_file))
    logger.warning.assert_called_with(
        'Skipping {filename} due to decoding error: {error}'.format(
            filename=binary_file,
            error="'{encoding}' codec can't decode byte 0xff in position 0:\
 invalid start byte".format(encoding=ENCODING)
        )
    )


def test_is_script_binary_file(mocker, binary_file):
    logger = Mock()
    mocker.patch('important.parse.logger', logger)

    # Make the file executable to appear to be a script
    os.chmod(binary_file, stat.S_IXUSR | stat.S_IRUSR)
    # Attempt to parse and assert that it logged a warning
    _is_script(binary_file)
    logger.warning.assert_called_with(
        'Skipping {filename} due to decoding error: {error}'.format(
            filename=binary_file,
            error="'{encoding}' codec can't decode byte 0xff in position 0:\
 invalid start byte".format(encoding=ENCODING)
        )
    )


def test_dir_imports(python_source_dir, python_file_imports, exclusions):
    assert set(parse_dir_imports(python_source_dir, exclusions)) == \
        set(python_file_imports)


def test_excluded_directory_imports(python_excluded_dir, exclusions):
    assert set(parse_dir_imports(python_excluded_dir, exclusions)) == set()


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
            parse_requirements(str(requirements_file))] == \
        ['pkg1', 'pkg2', 'pkg3', 'SomeDependency']


def test_requirements_without_name(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
git+https://myvcs.com/some_dependency@sometag
    '''.strip())
    with pytest.raises(ValueError) as excinfo:
        list(parse_requirements(str(requirements_file)))
    assert str(excinfo.value) == \
        'A requirement lacks a name (e.g. no `#egg` url)'


def test_requirements_editable(tmpdir):
    requirements_file = tmpdir.join('requirements.txt')
    requirements_file.write('''
-e git+https://myvcs.com/some_dependency@sometag#egg=SomeDependency
    '''.strip())
    with pytest.raises(ValueError) as excinfo:
        list(parse_requirements(str(requirements_file)))
    assert str(excinfo.value) == \
        'Cannot parse SomeDependency: editable projects unsupported'


def test_translate_requirement_to_module_names(mocker):
    logger = Mock()
    mocker.patch('important.parse.logger', logger)

    assert translate_requirement_to_module_names('click') == set(['click'])
    logger.warning.assert_not_called()

    logger.reset_mock()
    assert translate_requirement_to_module_names('not_a_real_package') == \
        set(['not_a_real_package'])
    logger.warning.assert_called_with("Cannot find install location of \
'not_a_real_package'; please install this package for more accurate name \
resolution")

    logger.reset_mock()
    assert translate_requirement_to_module_names('pip') == set(['pip'])
    logger.warning.assert_not_called()

    logger.reset_mock()
    assert translate_requirement_to_module_names('dnspython') == set(['dns'])
    logger.warning.assert_not_called()

    logger.reset_mock()
    assert translate_requirement_to_module_names('fake') == set(['fake'])
    logger.warning.assert_called_with("Cannot find install location of \
'fake'; please install this package for more accurate name resolution")

    logger.reset_mock()
    assert translate_requirement_to_module_names('os.path') == set(['os.path'])
    logger.warning.assert_not_called()

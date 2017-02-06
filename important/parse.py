# Copyright (c) 2016-2017 Chris Fournier. All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found
# in the LICENSE file.
from __future__ import unicode_literals

import ast
import io
import logging
import os
import pkgutil
import re
import stat
import sys

from collections import namedtuple
from itertools import chain

import pip

from pip.commands.show import search_packages_info
from pip.req import parse_requirements as pip_parse_requirements


RE_SHEBANG = re.compile('^#![^\n]*python[0-9]?$')
ALL_MODULES = set(
    m[1] for m in pkgutil.iter_modules()) | set(
        sys.builtin_module_names)

Import = namedtuple('Import', ['module', 'filename', 'lineno', 'col_offset'])

LOGGER = logging.getLogger()


def _imports(source, filepath):
    def _ast_imports(root):
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.ImportFrom):
                yield (node.module, node.lineno, node.col_offset)
            elif isinstance(node, ast.Import):
                for name in node.names:
                    yield (name.name, node.lineno, node.col_offset)
            else:
                for statement in _ast_imports(node):
                    yield statement
    root = ast.parse(source, filename=filepath)
    for statement in _ast_imports(root):
        yield statement


def is_excluded(path, exclusions):
    if exclusions:
        for _ in chain(
                (e for e in exclusions if os.path.samefile(path, e)),
                (e for e in exclusions if
                 os.path.samefile(os.path.dirname(path), e)),
        ):
            return True
    return False


def parse_file_imports(filepath, exclusions=None, directory=None):
    # Skip if this file is supposed to be excluded
    if is_excluded(filepath, exclusions):
        return
    # Create a directory to report filepaths relative to
    if directory is None:
        directory = os.path.dirname(filepath)
    display_filepath = os.path.relpath(filepath, directory)
    # Compile and parse abstract syntax tree and find import statements
    try:
        with io.open(filepath) as handle:
            source = handle.read()
        # Remove lines with only comments (e.g. PEP 263 encodings)
        source = '\n'.join(
            '' if l.startswith('#') else l for l in source.split('\n'))
        # Parse
        for statement in _imports(source, filepath):
            module, lineno, col_offset = statement
            yield Import(module, display_filepath, lineno, col_offset)
    except SyntaxError as exc:
        LOGGER.warning('Skipping %s due to syntax error: %s',
                       exc.filename, str(exc))
    except UnicodeDecodeError as exc:
        LOGGER.warning('Skipping %s due to decode error: %s',
                       filepath, str(exc))


def _is_script(filepath):
    if os.access(filepath, os.F_OK | os.R_OK | os.X_OK) and \
       not stat.S_ISSOCK(os.stat(filepath).st_mode):
        try:
            with io.open(filepath, mode='r') as handle:
                first_line = handle.readline()
            return bool(RE_SHEBANG.match(first_line))
        except UnicodeDecodeError as exc:
            LOGGER.warning(
                'Skipping %s due to decode error: %s', filepath, str(exc))
    return False


def parse_dir_imports(current_directory, exclusions=None):
    # Skip if this directory is supposed to be excluded
    if is_excluded(current_directory, exclusions):
        return
    # Iterate over all Python/script files
    for root, dirs, files in os.walk(current_directory, topdown=True):
        dirs[:] = [os.path.join(root, d) for d in dirs if d not in exclusions]
        for filename in files:
            filename = filename.decode('utf-8') \
                if hasattr(filename, 'decode') and isinstance(filename, str) \
                else filename
            filepath = os.path.join(root, filename)
            if filename.endswith('.py') or _is_script(filepath):
                for statement in parse_file_imports(filepath, exclusions,
                                                    current_directory):
                    yield statement


def parse_requirements(filename):
    requirements = pip_parse_requirements(filename,
                                          session=pip.download.PipSession())
    for requirement in requirements:
        if not requirement.name:
            raise ValueError(
                'A requirement lacks a name (e.g. no `#egg` url)')
        elif requirement.editable:
            raise ValueError(
                'Cannot parse %s: editable projects unsupported' %
                requirement.name)
        else:
            yield requirement


def translate_req_to_module_names(requirement_name):
    provides = set()

    def is_module_folder(filepath):
        return bool(filepath) and \
            '/' not in filepath and \
            '.egg-info' not in filepath and \
            '.dist-info' not in filepath and \
            '__pycache__' not in filepath

    def is_top_level_file(filepath):
        return bool(filepath) and \
            '/' not in filepath and \
            filepath.endswith('.py')

    for result in search_packages_info([requirement_name]):
        if 'files' not in result or not result['files']:
            # Assume that only one module is installed in this case
            continue
        # Handle modules that are installed as folders in site-packages
        folders = [os.path.dirname(filepath) for filepath in result['files']]
        folders = filter(is_module_folder, folders)
        provides |= set(folders)
        # Handle modules that are installed as .py files in site-packages
        top_level_files = filter(is_top_level_file, result['files'])
        provides |= set([os.path.splitext(filename)[0]
                         for filename in top_level_files])

    if provides:
        return provides
    else:
        module_name = requirement_name.split('.')[0]
        if module_name not in ALL_MODULES:
            LOGGER.warning("Cannot find install location of '%s'; please \
install this package for more accurate name resolution", requirement_name)
        return provides if provides else set([requirement_name])

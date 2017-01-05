from __future__ import unicode_literals

import ast
import logging
import os
import pip
import pkgutil
import re
import stat
import sys

from collections import namedtuple
from io import open
from pip.commands.show import search_packages_info
from pip.req import parse_requirements as pip_parse_requirements


RE_SHEBANG = re.compile('^#![^\n]*python[0-9]?$')
ALL_MODULES = set(
    m[1] for m in pkgutil.iter_modules()) | set(
        sys.builtin_module_names)

Import = namedtuple('Import', ['module', 'filename', 'lineno', 'col_offset'])

logger = logging.getLogger()


def _imports(source):
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
    for statement in _ast_imports(ast.parse(source)):
        yield statement


def is_excluded(path, exclusions):
    if exclusions:
        generators = (
            filter(lambda e: os.path.samefile(path, e), exclusions),
            filter(lambda e: os.path.samefile(os.path.dirname(path), e),
                   exclusions)
        )
        for generator in generators:
            for _ in generator:
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
        with open(filepath) as fh:
            source = fh.read()
        # Remove lines with only comments (e.g. PEP 263 encodings)
        source = '\n'.join(
            map(
                lambda l: '' if l.startswith('#') else l,
                source.split('\n')
            )
        )
        # Parse
        statements = ast.parse(source, filename=filepath)
        for statement in _imports(statements):
            module, lineno, col_offset = statement
            yield Import(module, display_filepath, lineno, col_offset)
    except SyntaxError as e:
        logger.warning('Skipping {filename} due to syntax error: {error}'
                       .format(filename=e.filename, error=str(e)))
    except UnicodeDecodeError as e:
        logger.warning('Skipping {filename} due to decoding error: {error}'
                       .format(filename=filepath, error=str(e)))


def _is_script(filepath):
    if os.access(filepath, os.F_OK | os.R_OK | os.X_OK) and \
       not stat.S_ISSOCK(os.stat(filepath).st_mode):
        try:
            with open(filepath, mode='r') as fh:
                first_line = fh.readline()
            return bool(RE_SHEBANG.match(first_line))
        except UnicodeDecodeError as e:
            logger.warning('Skipping {filename} due to decoding error: {error}'
                           .format(filename=filepath, error=str(e)))
    return False


def parse_dir_imports(current_directory, exclusions=None):
    # Skip if this directory is supposed to be excluded
    if is_excluded(current_directory, exclusions):
        return
    # Iterate over all Python/script files
    for root, dirs, files in os.walk(current_directory, topdown=True):
        dirs[:] = filter(lambda d: d not in exclusions,
                         [os.path.join(root, d) for d in dirs])
        for filename in files:
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


def translate_requirement_to_module_names(requirement_name):
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
        # Handle modules that are installed as folders in site-packages
        folders = map(lambda filepath: os.path.dirname(filepath),
                      result['files'])
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
            logger.warning("Cannot find install location of '{requirement}'; please \
install this package for more accurate name resolution"
                           .format(requirement=requirement_name))
        return provides if provides else set([requirement_name])

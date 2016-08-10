import ast
import os
import pip
import re
from collections import namedtuple

RE_SHEBANG = re.compile('^#![^\n]*python[0-9]?$')

Import = namedtuple('Import', ['module', 'filename', 'lineno', 'col_offset'])


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


def parse_file_imports(filepath, directory=None):
    if directory is None:
        directory = os.path.dirname(filepath)
    display_filepath = os.path.relpath(filepath, directory)
    with open(filepath) as fh:
        source = fh.read()
    for statement in _imports(ast.parse(source)):
        module, lineno, col_offset = statement
        yield Import(module, display_filepath, lineno, col_offset)


def _is_script(filepath):
    if os.access(filepath, os.X_OK):
        with open(filepath, 'r') as fh:
            first_line = fh.readline()
        return bool(RE_SHEBANG.match(first_line))
    return False


def parse_dir_imports(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith('.py') or _is_script(filepath):
                for statement in parse_file_imports(filepath, directory):
                    yield statement


def parse_requirements(filename):
    requirements = pip.req.parse_requirements(filename,
                                              session=pip.download.PipSession())
    for requirement in requirements:
        if not requirement.name:
            raise ValueError(
                'A requirement lacks a name (e.g. no `#egg` on a `file:` path)')
        elif requirement.editable:
            raise ValueError(
                'Cannot parse %s: editable projects unsupported' %
                requirement.name)
        else:
            yield requirement

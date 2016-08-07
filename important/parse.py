import ast
import os
import pip
import re
from collections import namedtuple

RE_SHEBANG = re.compile('^#![^\n]*python[0-9]?$')

import_statement = namedtuple('import_statement', ['module', 'filename', 'lineno'])


def _imports(source):
    def _ast_imports(root):
        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.ImportFrom):
                yield (node.module, node.lineno)
            elif isinstance(node, ast.Import):
                for name in node.names:
                    yield (name.name, node.lineno)
            else:
                for statement in _ast_imports(node):
                    yield statement
    for statement in _ast_imports(ast.parse(source)):
        yield statement


def parse_file_imports(filename):
    with open(filename) as fh:
        source = fh.read()
    for statement in _imports(ast.parse(source)):
        yield statement


def _is_script(filepath):
    if os.access(filepath, os.X_OK):
        with open(filepath, 'r') as fh:
            first_line = fh.readline()
        return bool(RE_SHEBANG.match(first_line))
    return False


def parse_dir_imports(directory):
    for root, dir, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith('.py') or _is_script(filepath):
                display_filepath = os.path.relpath(filepath, directory)
                for statement in parse_file_imports(filepath):
                    module, lineno = statement
                    yield import_statement(module, display_filepath, lineno)


def _req_has_file_link(req):
    url = getattr(req, 'url', None)
    if url and url.lower().startswith('file:'):
        return True
    link = getattr(req, 'link', None)
    if link and getattr(link, 'scheme', '') == 'file':
        return True
    return False


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
        elif _req_has_file_link(requirement):
            raise ValueError(
                'Cannot parse %s: file-specified projects unsupported' %
                requirement.name)
        else:
            yield requirement


def parse_requirement_contraints(filename):
    for requirement in parse_requirements(filename):
        pass

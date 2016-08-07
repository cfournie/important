import os
import pkgutil
import sys
from collections import defaultdict

def base_module_name(import_statement):
    return import_statement.module.split('.')[0]


def check_unused_requirements(imports, requirements):
    # Parse base imports
    imports = set(base_module_name(import_statement) \
                  for import_statement in imports)
    requirements = set(requirements)
    return requirements - imports


def _get_module_containing_dir(module):
    loader = pkgutil.get_loader(module)
    if loader:
        return os.path.dirname(os.path.relpath(loader.path, sys.prefix))


def frequency_count_imports(imports):
    known_stdlib = set(sys.builtin_module_names)
    module_frequencies = defaultdict(int)
    base_module_frequencies = defaultdict(int)

    os_containing_dir = _get_module_containing_dir('os')

    def is_stdlib(import_statement):
        module = base_module_name(import_statement)
        if module in known_stdlib:
            return True
        elif module in base_module_frequencies:
            return False
        elif _get_module_containing_dir(module) == os_containing_dir:
            known_stdlib.add(module)
            return True

    for import_statement in imports:
        if not is_stdlib(import_statement):
            module_frequencies[import_statement.module] += 1
            base_module_frequencies[
                _get_module_containing_dir(import_statement.module)
            ] += 1

    return module_frequencies, base_module_frequencies


def check_import_frequencies(imports, contraints):
    pass

from collections import defaultdict

def _base_module_name(import_statement):
    return import_statement.module.split('.')[0]


def check_unused_requirements(imports, requirements):
    # Parse base imports
    imports = set(_base_module_name(import_statement) \
                  for import_statement in imports)
    requirements = set(requirement.name.lower() for requirement in requirements)
    return requirements - imports


def frequency_count_imports(imports):
    module_frequencies = defaultdict(int)
    base_module_frequencies = defaultdict(int)
    for import_statement in imports:
        module_frequencies[import_statement.module] += 1
        base_module_frequencies[
            _base_module_name(import_statement)
        ] += 1
    return module_frequencies, base_module_frequencies


def check_import_frequencies(imports, contraints):
    pass

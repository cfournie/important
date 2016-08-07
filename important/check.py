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
    for import_statement in imports:
        module_frequencies[import_statement.module] += 1
        if '.' in import_statement.module:
            module_frequencies[
                _base_module_name(import_statement)
            ] += 1
    return module_frequencies


def check_import_frequencies(imports, requirements):
    constraints = dict()
    for requirement in requirements:
        if requirement.req.specifier:
            constraints[requirement.name] = requirement.req.specifier
    module_frequencies = frequency_count_imports(imports)
    violations = dict()
    for module, constraint in constraints.items():
        if module in module_frequencies \
            and not constraint.contains(str(module_frequencies[module])):
            violations[module] = (constraint, module_frequencies[module])
    return violations

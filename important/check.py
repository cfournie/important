from collections import defaultdict
from important.parse import translate_requirement_to_module_names


def _base_module_name(import_statement):
    return import_statement.module.split('.')[0]


def check_unused_requirements(imports, requirements):
    # Parse base imports
    imports = set(_base_module_name(import_statement)
                  for import_statement in imports)
    requirements = set(requirement.name for requirement in requirements)
    module_requirements = {}
    all_modules = set()
    for requirement in requirements:
        modules = translate_requirement_to_module_names(requirement)
        for module in modules:
            module_requirements[module] = requirement
        all_modules |= modules
    unused_modules = all_modules - imports
    return set(map(lambda module: module_requirements[module], unused_modules))


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
    for requirement, constraint in constraints.items():
        modules = translate_requirement_to_module_names(requirement)
        for module in modules:
            if module in module_frequencies \
                    and not constraint.contains(
                        str(module_frequencies[module])):
                violations[requirement] = (constraint,
                                           module_frequencies[module])
    return violations

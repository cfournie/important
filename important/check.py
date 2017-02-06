# Copyright (c) 2016-2017 Chris Fournier. All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found
# in the LICENSE file.
from __future__ import unicode_literals

from collections import defaultdict
from important.parse import translate_req_to_module_names


def _base_module_name(import_statement):
    return import_statement.module.split('.')[0]


def check_unused_requirements(imports, requirements):
    # Parse base imports
    imports = set(_base_module_name(import_statement)
                  for import_statement in imports)
    requirements = set(requirement.name for requirement in requirements)
    # Translate package names into module names that can be imported
    module_requirements = {}
    for requirement in requirements:
        modules = translate_req_to_module_names(requirement)
        for module in modules:
            module_requirements[module] = requirement
    # Translate imported modules into package names
    imports_as_requirements = set(
        (module_requirements.get(module, module) for module in imports)
    )
    # Find those required packages that were not imported
    return requirements - imports_as_requirements


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
        modules = translate_req_to_module_names(requirement)
        for module in modules:
            if module in module_frequencies and not constraint.contains(
                    str(module_frequencies[module])):
                violations[requirement] = (constraint,
                                           module_frequencies[module])
    return violations

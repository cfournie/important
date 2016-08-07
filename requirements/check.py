def check_unused_requirements(imports, requirements):
    # Parse base imports
    imports = set(import_statement.module.split('.')[0] \
                  for import_statement in imports)
    requirements = set(requirements)
    return requirements - imports

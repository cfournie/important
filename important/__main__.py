import click
import os
import sys
from requirements.parse import parse_dir_imports, parse_file_imports, \
    parse_requirements
from requirements.check import check_unused_requirements

@click.command()
@click.argument('requirements')
@click.argument('sourcecode', nargs=-1)
def check(requirements, sourcecode):
    # Parse requirements
    requirements=parse_requirements(requirements)
    # Parse source code
    imports = list()
    for path in sourcecode:
        if os.path.isfile(path):
            imports.extend(parse_file_imports(path))
        elif os.path.isdir(path):
            imports.extend(parse_dir_imports(path))
        else:
            raise Exception('%s does not exist' % path)
    # Test
    unused_requirements = check_unused_requirements(imports, requirements)
    for unused_requirement in unused_requirements:
        sys.stderr.write('%s\n' % unused_requirement)
    if unused_requirements:
        sys.exit(1)


if __name__ == '__main__':
    check()

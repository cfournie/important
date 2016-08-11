import click
from click import ClickException
import os
from important.parse import parse_dir_imports, parse_file_imports, \
    parse_requirements
from important.check import check_unused_requirements, check_import_frequencies
import sys


@click.command('Check imports within sourcecode for either unused requirements'
               ' or an import frequency that violates some constraints')
@click.option('--requirements',
              multiple=True,
              help="Requirement(s) file(s) to check for unused entries by "
                   "comparing against imports in source code; for formatting, "
                   "see pip's documentation https://pip.pypa.io/",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True,
                              resolve_path=True))
@click.option('--constraints',
              help="Requirement(s) file(s) to interpret as constraints on the "
                   "frequency of imports in source code.  Version numbers are "
                   "interpreted as frequency constraints, e.g., `os.path<5` "
                   "requires that there be no more than 4 imports of the "
                   "`os.path` module in the sourcecode.  Multiple constraints "
                   "can be added using commas, e.g. `os>=1,<=5` meaning that "
                   "sourcecode must contain one or more but 5 or less imports "
                   "of `os`."
                   "This can be used to slowly wean a project off of a module "
                   "(e.g. while converting a large project from Python 2 to 3)"
                   " or to prevent a module from being used altogether using "
                   "`os.path==0`."
                   "Note that when frequency counting, imports of `os.path` "
                   "and `os` will produce a frequency of `os==2` and `os.path"
                   "==1`",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True,
                              resolve_path=True))
@click.option('-v', '--verbose', count=True)
@click.argument('sourcecode', nargs=-1,
                type=click.Path(exists=True, file_okay=True, dir_okay=True,
                                writable=False, readable=True,
                                resolve_path=True))
def check(requirements, constraints, verbose, sourcecode):
    # Parse requirements and contraints
    parsed_requirements = []
    for requirements_path in requirements:
        parsed_requirements.extend(parse_requirements(requirements_path))
    parsed_contraints = parse_requirements(constraints)

    # Parse source code
    imports = []
    for path in sourcecode:
        if os.path.isfile(path):
            imports.extend(parse_file_imports(path))
        elif os.path.isdir(path):
            imports.extend(parse_dir_imports(path))

    output = []

    # Test requirements
    unused_requirements = None
    if parsed_requirements:
        unused_requirements = check_unused_requirements(imports,
                                                        parsed_requirements)
        if verbose > 0:
            for unused_requirement in sorted(unused_requirements):
                output.append('%s (unused requirement)' % unused_requirement)

    # Test contraints
    contraint_violations = None
    if constraints:
        contraint_violations = check_import_frequencies(imports,
                                                        parsed_contraints)
        if verbose > 0:
            for module, violation in sorted(contraint_violations.items()):
                constraint, frequency = violation
                output.append('%s%s (constraint violated by %s==%d)' %
                              (module, constraint, module, frequency))

    # Exit
    if unused_requirements or contraint_violations:
        if verbose:
            message = 'Unused requirements or violated contraints found'
            message += '\n' if output else ''
            message += '\n'.join(output) if output else ''
            raise ClickException(message)
        else:
            sys.exit(1)
    if not requirements and not constraints:
        raise ClickException('No checks performed; supply either requirements '
                             'or contraints')

if __name__ == '__main__':
    check()

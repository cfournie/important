# Copyright (c) 2016-2017 Chris Fournier. All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found
# in the LICENSE file.
import logging
import os
import sys

from configparser import ConfigParser

import click

from important.parse import parse_dir_imports, parse_file_imports, \
    parse_requirements
from important.check import check_unused_requirements, check_import_frequencies


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


# If a setup file exists, override cli arguments with those values
if os.path.exists('setup.cfg'):
    CONFIG = ConfigParser()
    CONFIG.read('setup.cfg')

    def split(key_value):
        if key_value[0] in ('sourcecode',):
            return key_value
        else:
            return key_value[0], key_value[1].split()

    CONTEXT_SETTINGS['default_map'] = \
        dict(map(split, CONFIG.items('important')))


@click.command(help="Check imports within SOURCECODE (except those files "
                    "provided in EXCLUDE) for either unused requirements or "
                    "an import frequency that violates some constraints.",
               context_settings=CONTEXT_SETTINGS)
@click.option('--requirements', '-r', multiple=True,
              help="Requirement(s) file(s) to check for unused entries by "
                   "comparing against imports in source code; for formatting, "
                   "see pip's documentation https://pip.pypa.io/",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True,
                              resolve_path=True))
@click.option('--constraints', '-c', multiple=True,
              help="Requirement(s) file(s) to interpret as constraints on the "
                   "frequency of imports in source code.  Version numbers are "
                   "interpreted as frequency constraints, e.g., `os.path<5` "
                   "requires that there be no more than 4 imports of the "
                   "`os.path` module in the sourcecode.  Multiple constraints "
                   "can be added using commas, e.g. `os>=1,<=5` meaning that "
                   "sourcecode must contain one or more but 5 or less imports "
                   "of `os`. "
                   "This can be used to slowly wean a project off of a module "
                   "(e.g. while converting a large project from Python 2 to 3)"
                   " or to prevent a module from being used altogether using "
                   "`os.path==0`. "
                   "Note that when frequency counting, imports of `os.path` "
                   "and `os` will produce a frequency of `os==2` and `os.path"
                   "==1`",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True,
                              resolve_path=True))
@click.option('--ignore', '-i', multiple=True,
              help="Requirement names to ignore when searching for unused "
                   "requirements")
@click.option('--ignorefile', multiple=True,
              help="Requirement(s) to ignore specified in requirements files",
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True,
                              resolve_path=True))
@click.option('--exclude', '-e', multiple=True,
              help="Python files or directories to exclude from analysis",
              type=click.Path(exists=True, file_okay=True, dir_okay=True,
                              writable=False, readable=True,
                              resolve_path=True))
@click.argument('sourcecode', nargs=1,
                type=click.Path(exists=True, file_okay=True, dir_okay=True,
                                writable=False, readable=True,
                                resolve_path=True))
@click.option('-v', '--verbose', count=True)
def check(requirements, constraints, ignore, ignorefile, exclude, sourcecode,
          verbose):
    # Validate options
    if not requirements and not constraints:
        raise click.BadParameter('no checks performed; supply either '
                                 '--requirements or --contraints')

    # Parse requirements and contraints
    parsed_requirements = []
    for requirements_path in requirements:
        parsed_requirements.extend(parse_requirements(requirements_path))
    parsed_contraints = []
    for contraints_path in constraints:
        parsed_contraints.extend(parse_requirements(contraints_path))

    # Remove requirements that are ignored
    ignore = list(ignore)
    for ignorefile_path in ignorefile:
        ignore.extend(
            (r.name for r in parse_requirements(ignorefile_path))
        )
    if ignore:
        parsed_requirements = [r for r in parsed_requirements
                               if r.name not in ignore]

    if verbose >= 2:
        click.echo('Read requirements:')
        for parsed_requirement in sorted(parsed_requirements,
                                         key=lambda r: r.name):
            click.echo(parsed_requirement.name)
        click.echo('Read constraints:')
        for parsed_contraint in sorted(parsed_contraints,
                                       key=lambda r: r.name):
            click.echo('{constraint}{specifier}'.format(
                constraint=parsed_contraint.name,
                specifier=str(parsed_contraint.specifier)))

    # Parse source code
    imports = None
    if os.path.isfile(sourcecode):
        imports = set(parse_file_imports(sourcecode, exclude))
    elif os.path.isdir(sourcecode):
        imports = set(parse_dir_imports(sourcecode, exclude))
    else:
        raise click.BadParameter("could not parse SOURCECODE '%s'; path is "
                                 "either not a file or not a directory" %
                                 sourcecode)
    filenames = set(i.filename for i in imports)

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
            for module, violation in sorted(
                    contraint_violations.items(),
                    key=lambda module_violation: module_violation[0]
            ):
                constraint, frequency = violation
                output.append('%s%s (constraint violated by %s==%d)' %
                              (module, constraint, module, frequency))

    # Statistics
    if verbose >= 1:
        click.echo('Parsed {imports} imports in {files} files'.format(
            imports=len(imports),
            files=len(filenames),
        ))
    if verbose >= 3:
        for filename in sorted(filenames):
            click.echo(filename)
        for i in sorted(imports):
            click.echo('{module}={filename}:{lineno}'.format(
                module=i.module,
                filename=i.filename,
                lineno=i.lineno))

    # Exit
    if unused_requirements or contraint_violations:
        if verbose >= 1:
            message = 'Unused requirements or violated constraints found'
            message += '\n' if output else ''
            message += '\n'.join(output) if output else ''
            raise click.ClickException(message)
        else:
            sys.exit(1)


if __name__ == '__main__':
    check()

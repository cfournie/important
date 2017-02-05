import codecs
import important.__main__
import os
import pytest
import re
import socket
import sys
import tempfile

from configparser import ConfigParser
from click.testing import CliRunner


try:
    from importlib import reload
except:
    pass  # Python 2.7 provides reload built in

ENCODING = 'utf-8' if sys.version_info > (3, 0) else 'utf8'


def run_check(requirements=None, constraints=None, ignore=None,
              ignorefile=None, verbose=0, exclude=None, sourcecode=None,
              use_setupcfg=False, tmpdir=None):
    # Compose args
    runner_args = []
    setup_cfg = {}
    setup_cfg_args = []
    if requirements:
        for requirements_file in requirements:
            runner_args.extend(['--requirements', requirements_file])
        setup_cfg['requirements'] = requirements
    if constraints:
        for constraints_file in constraints:
            runner_args.extend(['--constraints', constraints_file])
        setup_cfg['constraints'] = constraints
    if ignore:
        for ignored_requirement in ignore:
            runner_args.extend(['--ignore', ignored_requirement])
        setup_cfg['ignore'] = ignore
    if ignorefile:
        for ignorefile_path in ignorefile:
            runner_args.extend(['--ignorefile', ignorefile_path])
        setup_cfg['ignorefile'] = ignorefile
    if verbose:
        runner_args.append('-' + verbose * 'v')
        setup_cfg_args.append('-' + verbose * 'v')
    if exclude:
        runner_args.extend(exclude)
        setup_cfg['exclude'] = exclude
    runner_args.append(sourcecode)
    setup_cfg['sourcecode'] = sourcecode

    # Write a config file
    if use_setupcfg:
        config = ConfigParser()
        config.add_section('important')
        for key, value in setup_cfg.items():
            if key not in ('sourcecode',):
                value = '\n'.join(value)
            config.set('important', key, value)
        filepath = str(tmpdir.join('setup.cfg'))
        with codecs.open(filepath, 'w', encoding=ENCODING) as f:
            config.write(f)

    # Run cli
    runner = CliRunner()
    cwd = os.getcwd()
    try:
        # Change the cwd and reload the module to alter the defaults to come
        # from the new cwd
        os.chdir(str(tmpdir))
        reload(important.__main__)
        if use_setupcfg:
            return runner.invoke(important.__main__.check, setup_cfg_args,
                                 catch_exceptions=False)
        else:
            return runner.invoke(important.__main__.check, runner_args,
                                 catch_exceptions=False)
    finally:
        os.chdir(cwd)


def format_output(*output, **kwargs):
    package_name = kwargs.get('package_name')
    import_name = kwargs.get('import_name')

    def sort_output(output, package_name):
        """ Format and sort output by requirement/constraint package names """
        if package_name and package_name in output or \
           import_name and import_name in output:
            return '\n'.join(
                sorted(
                    output.strip().split('\n'),
                    key=lambda l: re.split('[\<\>\= ]+', l, maxsplit=1)[0]
                )
            )
        else:
            return output

    return '\n'.join(
        (sort_output(
            output=part.strip().format(**kwargs),
            package_name=package_name) for part in output)) + '\n'


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_just_requirements(requirements_file, python_source_dir,
                                python_excluded_file, python_excluded_dir,
                                setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file,),
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 0, result.output
    assert result.output == ''


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_just_constraints(constraints_file, python_source_dir,
                               python_excluded_file, python_excluded_dir,
                               setupcfg, tmpdir):
    result = run_check(
        constraints=(constraints_file,),
        verbose=0,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 0, result.output
    assert result.output == ''


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_verbosity_level_0(requirements_file, constraints_file,
                                python_source_dir, python_excluded_file,
                                python_excluded_dir, setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file,),
        constraints=(constraints_file,),
        verbose=0,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 0, result.output
    assert result.output == ''


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_verbosity_level_1(requirements_file, constraints_file,
                                python_source_dir, python_excluded_file,
                                python_excluded_dir, python_imports,
                                python_files_parsed, setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file,),
        constraints=(constraints_file,),
        verbose=1,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 0, result.output
    assert result.output == '''
Parsed {num_imports} imports in {num_files} files
'''.lstrip().format(
        num_imports=len(python_files_parsed) * len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_verbosity_level_2(requirements_file, constraints_file,
                                python_source_dir, python_excluded_file,
                                python_excluded_dir, package_name,
                                python_imports, python_files_parsed,
                                setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file,),
        constraints=(constraints_file,),
        verbose=2,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 0, result.output
    assert result.output == format_output(
        '''
Read requirements:''',
        '''
csv
os
parser
{package_name}''',
        '''
Read constraints:''',
        '''
csv>1
{package_name}<=6
enum<10
os<=9
os.path<=6
other-unused==0
re<=3,>1
unused==0''',
        '''
Parsed {num_imports} imports in {num_files} files
''',
        package_name=package_name,
        num_imports=len(python_files_parsed) *
        len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_verbosity_level_3(requirements_file, constraints_file,
                                python_source_dir, python_excluded_file,
                                python_excluded_dir, package_name,
                                import_name, python_file_imports,
                                python_imports, python_files_parsed,
                                setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file,),
        constraints=(constraints_file,),
        verbose=3,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )

    imports = '\n'.join(
        '{module}={filename}:{lineno}'.format(
            module=import_object.module,
            filename=import_object.filename,
            lineno=import_object.lineno,
        )
        for import_object in sorted(
            python_file_imports,
            key=lambda r: (r.module, r.filename)
        )
    )

    assert result.exit_code == 0, result.output
    assert result.output == format_output(
        '''
Read requirements:''',
        '''
csv
os
parser
{package_name}''',
        '''
Read constraints:''',
        '''
csv>1
{package_name}<=6
enum<10
os<=9
os.path<=6
other-unused==0
re<=3,>1
unused==0''',
        '''
Parsed {num_imports} imports in {num_files} files
scriptfile
subdir/test3.py
test1.py''',
        imports,
        package_name=package_name,
        import_name=import_name,
        num_imports=len(python_files_parsed) *
        len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_error_verbosity_level_0(requirements_file_one_unused,
                                      constraints_file_package_disallowed,
                                      python_source_dir, python_excluded_file,
                                      python_excluded_dir, package_name,
                                      setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        verbose=0,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == ''


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_error_verbosity_level_1(requirements_file_one_unused,
                                      constraints_file_package_disallowed,
                                      python_source_dir, python_excluded_file,
                                      python_excluded_dir, package_name,
                                      python_imports, python_files_parsed,
                                      setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        verbose=1,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == format_output(
        '''
Parsed {num_imports} imports in {num_files} files
Error: Unused requirements or violated constraints found
unused (unused requirement)''', '''
{package_name}==0 (constraint violated by {package_name}==3)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)''',
        package_name=package_name,
        num_imports=len(python_files_parsed) * len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_ignored_error(requirements_file_one_unused,
                            constraints_file_package_disallowed,
                            python_source_dir, python_excluded_file,
                            python_excluded_dir, package_name,
                            python_imports, python_files_parsed,
                            setupcfg, tmpdir):
    # Test with ignore option
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        ignore=('unused',),
        verbose=1,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == format_output(
        '''
Parsed {num_imports} imports in {num_files} files
Error: Unused requirements or violated constraints found''', '''
{package_name}==0 (constraint violated by {package_name}==3)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)''',
        package_name=package_name,
        num_imports=len(python_files_parsed) * len(python_imports),
        num_files=len(python_files_parsed))

    # Create ignorefile
    ignorefile = tmpdir.join('ignore.txt')
    ignorefile.write('unused')
    ignorefile = str(ignorefile)

    # Test with ignorefile options
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        ignorefile=(ignorefile,),
        verbose=1,
        exclude=(
            python_excluded_file,
            python_excluded_dir,
        ),
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == format_output(
        '''
Parsed {num_imports} imports in {num_files} files
Error: Unused requirements or violated constraints found''', '''
{package_name}==0 (constraint violated by {package_name}==3)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)''',
        package_name=package_name,
        num_imports=len(python_files_parsed) * len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_error_just_dir(requirements_file_one_unused,
                             constraints_file_package_disallowed,
                             python_source_dir, package_name,
                             python_imports, python_files_parsed,
                             setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        verbose=1,
        sourcecode=python_source_dir,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == format_output(
        '''
Parsed {num_imports} imports in {num_files} files
Error: Unused requirements or violated constraints found
unused (unused requirement)''', '''
{package_name}==0 (constraint violated by {package_name}==3)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)''',
        package_name=package_name,
        num_imports=len(python_files_parsed) * len(python_imports),
        num_files=len(python_files_parsed))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_main_error_just_file(requirements_file_one_unused,
                              constraints_file_package_disallowed,
                              python_source_file, package_name,
                              python_imports, setupcfg, tmpdir):
    result = run_check(
        requirements=(requirements_file_one_unused,),
        constraints=(constraints_file_package_disallowed,),
        verbose=1,
        sourcecode=python_source_file,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 1
    assert result.output == format_output(
        '''
        Parsed {num_imports} imports in 1 files
Error: Unused requirements or violated constraints found
unused (unused requirement)''', '''
{package_name}==0 (constraint violated by {package_name}==1)
csv>1 (constraint violated by csv==1)
re<=3,>1 (constraint violated by re==1)
''', package_name=package_name, num_imports=len(python_imports))


@pytest.mark.parametrize('setupcfg', ('setupcfg', 'cliargs'))
def test_insufficient_args(python_source_file, setupcfg, tmpdir):
    result = run_check(
        sourcecode=python_source_file,
        use_setupcfg=setupcfg == 'setupcfg',
        tmpdir=tmpdir,
    )
    assert result.exit_code == 2
    assert result.output == ('''
Usage: check [OPTIONS] [EXCLUDE]... SOURCECODE

Error: Invalid value: no checks performed; supply either --requirements '''
                             '''or --contraints
'''.lstrip())


def test_socket(requirements_file, constraints_file):
    # Make our own temp dir because tmpdir's are too long to be unix sockets
    tempdir = tempfile.mkdtemp()
    socket_file = os.path.realpath(os.path.join(tempdir, 's'))
    try:
        python_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        python_socket.bind(str(socket_file))
        result = run_check(
            requirements=(requirements_file,),
            constraints=(constraints_file,),
            sourcecode=str(socket_file),
            tmpdir=tempdir,
        )
        assert result.exit_code == 2
        assert result.output == ('''
Usage: check [OPTIONS] [EXCLUDE]... SOURCECODE

Error: Invalid value: could not parse SOURCECODE '%s'; path is either not a '''
                                 '''file or not a directory
'''.lstrip() % str(socket_file))
    finally:
        python_socket.close()
        os.remove(socket_file)
        os.rmdir(tempdir)

from click.testing import CliRunner
from important.__main__ import check
import pytest
import socket


@pytest.fixture
def runner():
    return CliRunner()


def test_verbose(runner, requirements_file, constraints_file,
                 python_source_dir, python_excluded_file, python_excluded_dir):
    result = runner.invoke(check, ['--requirements', requirements_file,
                                   '--constraints', constraints_file,
                                   '--verbose', python_excluded_file,
                                   python_excluded_dir,
                                   python_source_dir],
                           catch_exceptions=False)
    assert result.exit_code == 1
    assert result.output == '''
Parsed 39 imports in 3 files
Error: Unused requirements or violated constraints found
pyyaml (unused requirement)
dnspython==0 (constraint violated by dnspython==3)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)\n'''.lstrip()


def test_dir_ok(runner, ok_requirements_file, ok_constraints_file,
                python_source_dir, python_excluded_file, python_excluded_dir):
    result = runner.invoke(check, ['--requirements', ok_requirements_file,
                                   '--constraints', ok_constraints_file,
                                   '--verbose', python_excluded_file,
                                   python_excluded_dir,
                                   python_source_dir],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == '''
Parsed 39 imports in 3 files
'''.lstrip()


def test_dir_ok_verbose2(runner, ok_requirements_file, ok_constraints_file,
                         python_source_dir, python_excluded_file,
                         python_excluded_dir):
    result = runner.invoke(check, ['--requirements', ok_requirements_file,
                                   '--constraints', ok_constraints_file,
                                   '-vv', python_excluded_file,
                                   python_excluded_dir,
                                   python_source_dir],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == '''
Read requirements:
os
csv
parser
dnspython
Read constraints:
unused ==0
other-unused ==0
os <=9
os.path <=6
dnspython <=6
enum <10
csv >1
re <=3,>1
Parsed 39 imports in 3 files
'''.lstrip()


def test_dir_ok_verbose3(runner, ok_requirements_file, ok_constraints_file,
                         python_source_dir, python_excluded_file,
                         python_excluded_dir):
    result = runner.invoke(check, ['--requirements', ok_requirements_file,
                                   '--constraints', ok_constraints_file,
                                   '-vvv', python_excluded_file,
                                   python_excluded_dir,
                                   python_source_dir],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output == '''
Read requirements:
os
csv
parser
dnspython
Read constraints:
unused ==0
other-unused ==0
os <=9
os.path <=6
dnspython <=6
enum <10
csv >1
re <=3,>1
Parsed 39 imports in 3 files
scriptfile
subdir/test3.py
test1.py
'''.lstrip()


def test_dir(runner, requirements_file, constraints_file, python_source_dir,
             python_excluded_file, python_excluded_dir):
    result = runner.invoke(check, ['--requirements', requirements_file,
                                   '--constraints', constraints_file,
                                   python_excluded_file,
                                   python_excluded_dir,
                                   python_source_dir],
                           catch_exceptions=False)
    assert result.exit_code == 1
    assert result.output == ''


def test_main_file(runner, requirements_file, constraints_file,
                   python_source_file):
    result = runner.invoke(check, ['--requirements', requirements_file,
                                   '--constraints', constraints_file,
                                   python_source_file],
                           catch_exceptions=False)
    assert result.exit_code == 1
    assert result.output == ''


def test_insufficient_args(runner, python_source_file):
    result = runner.invoke(check, [python_source_file],
                           catch_exceptions=False)
    assert result.exit_code == 2
    assert result.output == ('''
Usage: check [OPTIONS] [EXCLUDE]... SOURCECODE

Error: Invalid value: no checks performed; supply either --requirements '''
                             '''or --contraints
'''.lstrip())


def test_socket(runner, tmpdir, requirements_file, constraints_file):
    socket_file = tmpdir.join('s')
    try:
        python_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        python_socket.bind(str(socket_file))
        result = runner.invoke(check, ['--requirements', requirements_file,
                                       '--constraints', constraints_file,
                                       str(socket_file)],
                               catch_exceptions=False)
        assert result.exit_code == 2
        assert result.output == ('''
Usage: check [OPTIONS] [EXCLUDE]... SOURCECODE

Error: Invalid value: could not parse SOURCECODE '%s'; path is either not a '''
                                 '''file or not a directory
'''.lstrip() % str(socket_file))
    finally:
        python_socket.close()

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
Error: Unused requirements or violated constraints found
unused (unused requirement)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)\n'''.lstrip()


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

import pytest
from important.__main__ import check
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


def test_main_verbose(runner, requirements_file, constraints_file,
                      python_source_file, python_source_dir):
    result = runner.invoke(check, ['--requirements', requirements_file,
                                   '--constraints', constraints_file,
                                   '--verbose',
                                   python_source_file, python_source_dir])
    assert result.exit_code == 1
    assert result.output == '''
Error: Unused requirements or violated contraints found
unused (unused requirement)
os<6 (constraint violated by os==9)
os.path<6 (constraint violated by os.path==6)\n'''.lstrip()


def test_main(runner, requirements_file, constraints_file, python_source_file,
              python_source_dir):
    result = runner.invoke(check, ['--requirements', requirements_file,
                                   '--constraints', constraints_file,
                                   python_source_file, python_source_dir])
    assert result.exit_code == 1
    assert result.output == ''


def test_main_insufficient_args(runner, requirements_file, constraints_file,
                                python_source_file, python_source_dir):
    result = runner.invoke(check, [python_source_file, python_source_dir])
    assert result.exit_code == 1
    assert result.output == '''
Error: No checks performed; supply either requirements or contraints
'''.lstrip()

import pytest
from important.__main__ import check
from click.testing import CliRunner


def test_main_unused_requirements(monkeypatch, python_source_file, requirements_file, constraints_file):
    #monkeypatch.setattr('sys.exit', lambda x: None)
    check()
    try:
        result = runner.invoke(check, [python_source_file, requirements_file, constraints_file], catch_exceptions=True)
    except:
        pass
    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'


def test_main_check_import_frequencies(monkeypatch, tmpdir, python_file_imports):
    assert False

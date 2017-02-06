# Copyright (c) 2016-2017 Chris Fournier. All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found
# in the LICENSE file.
from __future__ import unicode_literals

from important.parse import parse_requirements
from important.check import check_unused_requirements, \
    frequency_count_imports, check_import_frequencies
from pip._vendor.packaging.specifiers import SpecifierSet


def test_unused_requirements(python_file_imports,
                             requirements_file_one_unused):
    requirements = parse_requirements(requirements_file_one_unused)
    unused_requirements = check_unused_requirements(
        python_file_imports, requirements)
    assert set(unused_requirements) == {'unused'}


def test_frequency_count_imports(
        python_file_imports,
        import_name,
        python_files_parsed):
    expected = {
        '__future__': len(python_files_parsed),
        import_name: len(python_files_parsed),
        'collections': len(python_files_parsed),
        'copy': len(python_files_parsed) * 2,
        'csv': len(python_files_parsed),
        'enum': len(python_files_parsed),
        'math': len(python_files_parsed),
        'os': len(python_files_parsed) * 3,
        'os.path': len(python_files_parsed) * 2,
        'parser': len(python_files_parsed),
        're': len(python_files_parsed),
        'sys': len(python_files_parsed),
        'time': len(python_files_parsed),
    }
    # Also expect shorter forms of submodules (e.g. for `os.path` also
    # expect `os`)
    if '.' in import_name:
        for dots in range(1, import_name.count('.') + 1):
            new_import_name = '.'.join(import_name.split('.')[:dots])
            expected[new_import_name] = len(python_files_parsed)
    assert frequency_count_imports(python_file_imports) == expected


def test_check_import_frequencies(
        python_file_imports,
        constraints_file_package_disallowed,
        package_name):
    requirements = parse_requirements(constraints_file_package_disallowed)
    assert check_import_frequencies(python_file_imports, requirements) == {
        'os': (SpecifierSet('<6'), 9),
        'os.path': (SpecifierSet('<6'), 6),
        package_name: (SpecifierSet('==0'), 3),
    }
